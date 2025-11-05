from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class WorkOderClean(models.Model):
    _inherit = 'work.order.clean'


    frecuency_oport_related = fields.Many2one('frecuency.lead')
    wo_created_by_incident = fields.Boolean('Created by incident')


    # def action_finished(self):
    #     super(WorkOderClean, self).action_finished()
    #
    #     # Validar que los campos requeridos estén definidos
    #     if not self.start_date:
    #         raise UserError(_("The 'Start Date' field must be defined before finishing the work order."))
    #
    #     if not self.establishment_id:
    #         raise UserError(_("The 'Establishment' field must be defined to create a frequency lead."))
    #
    #     frecuency_lead_exists = self.env['frecuency.lead'].search_count([('previous_workorder_id', '=', self.id)])
    #
    #     notification = None
    #
    #     # Si complete_system es True, crear frecuencia
    #     if not frecuency_lead_exists and self.complete_system:
    #         frecuency_lead_vals = {
    #             'name': _('PENDING FRECUENCY LEAD - ') + self.establishment_id.name,
    #             'establishment_id': self.establishment_id.id,
    #             'previous_workorder_id': self.id,
    #             'calculated_date': self.start_date.date() + timedelta(days=self.establishment_id.delay),
    #             'last_workorder_date': self.start_date.date(),
    #         }
    #         new_frecuency_lead = self.env['frecuency.lead'].create(frecuency_lead_vals)
    #
    #         self.write({
    #             'frecuency_oport_related': new_frecuency_lead.id
    #         })
    #
    #         # Mensaje para notificación
    #         message = _(
    #             "Se ha creado una nueva oportunidad por frecuencia: %s") % new_frecuency_lead.name
    #
    #         notification = {
    #             'type': 'ir.actions.client',
    #             'tag': 'display_notification',
    #             'params': {
    #                 'title': _('OPORTUNIDAD CREADA'),
    #                 'message': message,
    #                 'sticky': True,
    #                 'type': 'success',
    #                 'next': {'type': 'ir.actions.act_window_close'},
    #                 'messageIsHtml': True
    #             }
    #         }
    #
    #     # Si complete_system es False y fue creado por incidente, verificar si expected_revenue <500
    #     elif not self.complete_system and self.wo_created_by_incident and self.lead_id and self.lead_id.expected_revenue < 500:
    #         # Buscar etapa de incidente
    #         stage_incident = self.env['crm.stage'].search([('incident', '=', True)])
    #         client_id = self.establishment_id.parent_id.parent_id
    #
    #         # Crear descripción para el incidente
    #         description = 'Lead created by OTL with expected revenue < 500 - OTL Origen ' + str(self.name or '')
    #
    #         # Datos para crear la oportunidad
    #         lead_data = {
    #             'name': _('Lead created by OTL with expected revenue < 500'),
    #             'partner_id': self.establishment_id.parent_id.id,
    #             'plant_ids': [(4, self.worksheet_ids.plant_id.id)],
    #             'type': 'opportunity',
    #             'stage_id': stage_incident.id,
    #             'wo_type': 'cleaning',
    #             'user_id': client_id.user_id.id if client_id and client_id.user_id else False,
    #             'description': description,
    #         }
    #
    #         # Crear la oportunidad
    #         new_lead = self.env['crm.lead'].create(lead_data)
    #
    #         # Mensaje para notificación
    #         message = _(
    #             "Se ha creado una nueva oportunidad por incidente: %s") % new_lead.name
    #
    #         notification = {
    #             'type': 'ir.actions.client',
    #             'tag': 'display_notification',
    #             'params': {
    #                 'title': _('OPORTUNIDAD CREADA'),
    #                 'message': message,
    #                 'sticky': True,
    #                 'type': 'success',
    #                 'next': {'type': 'ir.actions.act_window_close'},
    #                 'messageIsHtml': True
    #             }
    #         }
    #     # Si complete_system es False y fue creado por incidente, verificar si expected_revenue >=500
    #     elif not self.complete_system and self.wo_created_by_incident and self.lead_id and self.lead_id.expected_revenue >= 500:
    #         client_id = self.establishment_id.parent_id.parent_id
    #
    #         # Crear descripción para el incidente
    #         description = 'Lead created by OTL with expected revenue > 500 - OTL Origen ' + str(self.name or '')
    #
    #         # Datos para crear la oportunidad
    #         lead_data = {
    #             'name': _('Lead created by OTL with expected revenue > 500'),
    #             'partner_id': self.establishment_id.parent_id.id,
    #             'plant_ids': [(4, self.worksheet_ids.plant_id.id)],
    #             'type': 'opportunity',
    #             # 'stage_id': stage_incident.id,
    #             'wo_type': 'cleaning',
    #             'user_id': client_id.user_id.id if client_id and client_id.user_id else False,
    #             'description': description,
    #         }
    #
    #         # Crear la oportunidad
    #         new_lead = self.env['crm.lead'].create(lead_data)
    #
    #         # Mensaje para notificación
    #         message = _(
    #             "Se ha creado una nueva oportunidad por incidente: %s") % new_lead.name
    #
    #         notification = {
    #             'type': 'ir.actions.client',
    #             'tag': 'display_notification',
    #             'params': {
    #                 'title': _('OPORTUNIDAD CREADA'),
    #                 'message': message,
    #                 'sticky': True,
    #                 'type': 'success',
    #                 'next': {'type': 'ir.actions.act_window_close'},
    #                 'messageIsHtml': True
    #             }
    #         }
    #
    #     # Retornar notificación si existe
    #     if notification:
    #         return notification

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