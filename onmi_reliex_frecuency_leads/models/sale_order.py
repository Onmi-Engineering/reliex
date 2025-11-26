from odoo import fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    wo_clean_origin = fields.Many2one('work.order.clean')

    def action_confirm(self):
        """ Confirm the given quotation(s) and set their confirmation date.

        If the corresponding setting is enabled, also locks the Sale Order.

        :return: True
        :rtype: bool
        :raise: UserError if trying to confirm cancelled SO's
        """
        if not all(order._can_be_confirmed() for order in self):
            raise UserError(_(
                "The following orders are not in a state requiring confirmation: %s",
                ", ".join(self.mapped('display_name')),
            ))

        self.order_line._validate_analytic_distribution()

        for order in self:
            order.validate_taxes_on_sales_order()
            if order.partner_id in order.message_partner_ids:
                continue
            order.message_subscribe([order.partner_id.id])

        self.write(self._prepare_confirmation_values())

        context = self._context.copy()
        context.pop('default_name', None)
        context.pop('default_user_id', None)

        self.with_context(context)._action_confirm()

        self.filtered(lambda so: so._should_be_locked()).action_lock()

        if self.env.context.get('send_email'):
            self._send_order_confirmation_mail()

        # ========== GENERACION DE OTL Y PARTES ==========
        for order in self:
            # Solo generar si es tipo limpieza
            if hasattr(order, 'opportunity_wo_type') and order.opportunity_wo_type == 'cleaning':

                # Obtener el work.order.clean relacionado
                if not hasattr(order, 'wo_clean_origin') or not order.wo_clean_origin:
                    continue  # Si no hay OTL origen, saltar este pedido

                wo_clean_origin = order.wo_clean_origin

                # Obtener el establecimiento desde la OTL origen
                establishment_id = wo_clean_origin.establishment_id

                if not establishment_id:
                    continue  # Si no hay establecimiento, saltar

                if not establishment_id.parent_id:
                    raise UserError(_('The establishment must have a parent partner (main client).'))

                # Verificar si ya existe una OTL para este pedido
                existing_wo = self.env['work.order.clean'].search([
                    ('lead_id.order_ids', 'in', order.id)
                ], limit=1)

                if existing_wo:
                    continue  # Ya existe OTL, saltar este pedido

                # Obtener las instalaciones desde la OTL origen
                plant_ids = wo_clean_origin.related_plant_ids if wo_clean_origin.related_plant_ids else []

                # Crear el work.order.clean
                wo_clean_vals = {
                    'name': _('New'),
                    'partner_id': establishment_id.parent_id.id,  # Cliente principal
                    'establishment_id': establishment_id.id,  # Establecimiento desde OTL origen
                    'related_plant_ids': [(6, 0, plant_ids.ids)] if plant_ids else [],  # Instalaciones desde OTL origen
                    'lead_id': order.opportunity_id.id if order.opportunity_id else False,  # Oportunidad si existe
                    'user_id': order.user_id.id,  # Vendedor
                    'complete_system': order.complete_system if hasattr(order, 'complete_system') else False,
                    'cooker_hood': order.cooker_hood if hasattr(order, 'cooker_hood') else False,
                    'duct': order.duct if hasattr(order, 'duct') else False,
                    'extractor': order.extractor if hasattr(order, 'extractor') else False,
                    'filtronic': order.filtronic if hasattr(order, 'filtronic') else False,
                }

                wo_clean = self.env['work.order.clean'].sudo().create(wo_clean_vals)

                # Generar lìneas de materiales desde las líneas del pedido
                lines = self.env['materials']

                for sale_line in order.order_line.filtered(
                        lambda ol: ol.product_id and not ol.display_type):
                    # Agregar líneas al work.order.clean
                    wo_clean.sudo().write({
                        'line_ids': [(0, 0, {
                            'product_id': sale_line.product_id.id,
                            'quantity': sale_line.product_uom_qty,
                            'wo_clean_id': wo_clean.id,
                            'sale_order_line_id': sale_line.id
                        })]
                    })

                    # Crear registro en materials para usar después
                    lines += self.env['materials'].sudo().create({
                        'product_id': sale_line.product_id.id,
                        'quantity': sale_line.product_uom_qty,
                        'sale_order_line_id': sale_line.id,
                    })

                # Generar worksheet.part por cada instalación y día
                if plant_ids:
                    for plant in plant_ids:
                        # Verificar que la instalación tenga días de limpieza definidos
                        total_days = plant.days_clean if hasattr(plant, 'days_clean') else 1

                        # Crear un worksheet.part por cada día
                        for day in range(total_days):
                            part = self.env['worksheet.part'].sudo().create({
                                'name': _('New'),
                                'partner_id': establishment_id.parent_id.id,
                                'establishment_id': establishment_id.id,
                                'plant_id': plant.id,
                                'workorder_id': wo_clean.id,
                                'part_type': 'cleaning',
                                'allday': True,
                                'user_id': order.user_id.id,
                            })

                            # Agregar líneas de materiales a cada worksheet
                            for line in lines:
                                part.sudo().write({'cleaning_line_ids': [(0, 0, {
                                    'product_id': line.product_id.id,
                                    'sale_order_line_id': line.sale_order_line_id.id,
                                    'worksheet_id': part.id
                                })]})
        return True