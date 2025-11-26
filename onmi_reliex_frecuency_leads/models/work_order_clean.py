from odoo import fields, models, api, _
from odoo.exceptions import UserError


class WorkOderClean(models.Model):
    _inherit = 'work.order.clean'

    frecuency_oport_related = fields.Many2one('frecuency.lead')
    wo_created_by_incident = fields.Boolean('Created by incident')
    sale_order_related = fields.Many2one('sale.order')

    def action_finished(self):
        super(WorkOderClean, self).action_finished()

        # Validar que los campos requeridos estén definidos
        if not self.start_date:
            raise UserError(_("The 'Start Date' field must be defined before finishing the work order."))

        if not self.establishment_id:
            raise UserError(_("The 'Establishment' field must be defined to create a sale order."))

        # Verificar si ya existe un presupuesto relacionado
        sale_order_exists = self.env['sale.order'].search_count([
            ('origin', '=', self.name)
        ])

        notification = None

        # Si complete_system es True, crear presupuesto
        if not sale_order_exists and self.complete_system:
            # Obtener el cliente principal
            client_partner = self.establishment_id.parent_id

            # Obtener la lista de precios por defecto o la del cliente
            pricelist = self.establishment_id.property_product_pricelist or self.env['product.pricelist'].search([],
                                                                                                                 limit=1)

            sale_order_vals = {
                'partner_id': client_partner.id,  # Cliente principal
                'partner_shipping_id': self.establishment_id.id,  # Establecimiento como dirección de entrega
                'partner_invoice_id': client_partner.id,
                'complete_system': self.complete_system,
                'cooker_hood': self.cooker_hood,
                'duct': self.duct,
                'opportunity_wo_type': 'cleaning',
                'wo_clean_origin': self.id,
                'extractor': self.extractor,
                'filtronic': self.filtronic,
                'date_order': fields.Datetime.now(),
                'pricelist_id': pricelist.id,
                'origin': self.name,  # Referencia a la orden de trabajo
                'user_id': client_partner.user_id.id if client_partner.user_id else False,  # Usuario desde el cliente
                'note': _('Presupuesto generado automáticamente desde OTL: %s\n'
                          'Fecha del servicio: %s\n'
                          'Sistema completo realizado.') % (self.name, self.start_date.date()),
            }

            new_sale_order = self.env['sale.order'].create(sale_order_vals)

            # Buscar el producto con is_system_complete = True
            system_complete_product = self.env['product.product'].search([
                ('is_system_complete', '=', True)
            ], limit=1)

            if system_complete_product:
                # Crear la línea del pedido con el producto de sistema completo
                line_vals = {
                    'order_id': new_sale_order.id,
                    'product_id': system_complete_product.id,
                    'name': system_complete_product.display_name,
                    'product_uom_qty': 1,
                    'product_uom': system_complete_product.uom_id.id,
                    'price_unit': system_complete_product.list_price,
                    'tax_id': [(6, 0, system_complete_product.taxes_id.ids)],
                }

                # Crear la línea del pedido
                self.env['sale.order.line'].create(line_vals)

                # Agregar nota de servicio si no existe ya
                note_text = ("[SERVICIO] Aclaraciones del servicio:\n"
                             "-Equipo humano formado por dos técnicos, con amplia experiencia y formación.\n"
                             "-Equipos mecánicos adaptados para este tipo instalaciones.\n"
                             "-Limpieza de conductos realizada con cepillado neumático, siempre que sea la opción más óptima.*\n"
                             "-Espuma activa desengrasante.\n"
                             "-Plastificado de todas las zonas susceptibles a mancharse.\n"
                             "-Certificado administrativo de la limpieza.\n"
                             "-Subsanación in situ de cualquier deficiencia relacionada con el Sistema de extracción de humos (siempre que sea posible) y, en caso de no ser posible, valoración de la misma para su posterior reparación.\n"
                             "-Queda excluida la limpieza de los filtros de la/s campana/s.\n"
                             "-Verificación post venta de la calidad del servicio.")

                # Verificar si ya existe una nota con este contenido
                existing_note = new_sale_order.order_line.filtered(
                    lambda l: l.display_type == 'line_note' and '[SERVICIO] Aclaraciones del servicio:' in (l.name or '')
                )

                # Si no existe, crear la línea de nota
                if not existing_note:
                    note_vals = {
                        'order_id': new_sale_order.id,
                        'display_type': 'line_note',
                        'name': note_text,
                        'sequence': 9999,  # Para que aparezca al final
                    }
                    self.env['sale.order.line'].create(note_vals)

            else:
                raise UserError(_('No se encontró ningún producto con "Sistema Completo" activado. '
                                  'Por favor, configure un producto con el campo is_system_complete = True.'))

            # Mensaje para notificación
            message = _(
                "Se ha creado un nuevo presupuesto: %s para el cliente %s") % (
                          new_sale_order.name,
                          new_sale_order.partner_id.name
                      )

            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('PRESUPUESTO CREADO'),
                    'message': message,
                    'sticky': True,
                    'type': 'success',
                    'next': {'type': 'ir.actions.act_window_close'},
                    'messageIsHtml': True
                }
            }

        # Retornar notificación si existe
        if notification:
            return notification