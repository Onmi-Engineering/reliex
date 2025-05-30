from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class WorkOderClean(models.Model):
    _inherit = 'work.order.clean'


    frecuency_oport_related = fields.Many2one('frecuency.lead')
    wo_created_by_incident = fields.Boolean('Created by incident')


    def action_finished(self):
        super(WorkOderClean, self).action_finished()

        # Validar que los campos requeridos estén definidos
        if not self.start_date:
            raise UserError(_("The 'Start Date' field must be defined before finishing the work order."))

        if not self.establishment_id:
            raise UserError(_("The 'Establishment' field must be defined to create a frequency lead."))

        frecuency_lead_exists = self.env['frecuency.lead'].search_count([('previous_workorder_id', '=', self.id)])

        notification = None

        # Si complete_system es True, crear frecuencia
        if not frecuency_lead_exists and self.complete_system:
            frecuency_lead_vals = {
                'name': _('PENDING FRECUENCY LEAD - ') + self.establishment_id.name,
                'establishment_id': self.establishment_id.id,
                'previous_workorder_id': self.id,
                'calculated_date': self.start_date.date() + timedelta(days=self.establishment_id.delay),
                'last_workorder_date': self.start_date.date(),
            }
            new_frecuency_lead = self.env['frecuency.lead'].create(frecuency_lead_vals)

            self.write({
                'frecuency_oport_related': new_frecuency_lead.id
            })

            # Mensaje para notificación
            message = _(
                "Se ha creado una nueva oportunidad por frecuencia: %s") % new_frecuency_lead.name

            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('OPORTUNIDAD CREADA'),
                    'message': message,
                    'sticky': True,
                    'type': 'success',
                    'next': {'type': 'ir.actions.act_window_close'},
                    'messageIsHtml': True
                }
            }

        # Si complete_system es False y fue creado por incidente, verificar si expected_revenue <500
        elif not self.complete_system and self.wo_created_by_incident and self.lead_id and self.lead_id.expected_revenue < 500:
            # Buscar etapa de incidente
            stage_incident = self.env['crm.stage'].search([('incident', '=', True)])
            client_id = self.establishment_id.parent_id.parent_id

            # Crear descripción para el incidente
            description = 'Lead created by OTL with expected revenue < 500 - OTL Origen ' + str(self.name or '')

            # Datos para crear la oportunidad
            lead_data = {
                'name': _('Lead created by OTL with expected revenue < 500'),
                'partner_id': self.establishment_id.parent_id.id,
                'plant_ids': [(4, self.worksheet_ids.plant_id.id)],
                'type': 'opportunity',
                'stage_id': stage_incident.id,
                'wo_type': 'cleaning',
                'user_id': client_id.user_id.id if client_id and client_id.user_id else False,
                'description': description,
            }

            # Crear la oportunidad
            new_lead = self.env['crm.lead'].create(lead_data)

            # Mensaje para notificación
            message = _(
                "Se ha creado una nueva oportunidad por incidente: %s") % new_lead.name

            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('OPORTUNIDAD CREADA'),
                    'message': message,
                    'sticky': True,
                    'type': 'success',
                    'next': {'type': 'ir.actions.act_window_close'},
                    'messageIsHtml': True
                }
            }
        # Si complete_system es False y fue creado por incidente, verificar si expected_revenue >=500
        elif not self.complete_system and self.wo_created_by_incident and self.lead_id and self.lead_id.expected_revenue >= 500:
            client_id = self.establishment_id.parent_id.parent_id

            # Crear descripción para el incidente
            description = 'Lead created by OTL with expected revenue > 500 - OTL Origen ' + str(self.name or '')

            # Datos para crear la oportunidad
            lead_data = {
                'name': _('Lead created by OTL with expected revenue > 500'),
                'partner_id': self.establishment_id.parent_id.id,
                'plant_ids': [(4, self.worksheet_ids.plant_id.id)],
                'type': 'opportunity',
                # 'stage_id': stage_incident.id,
                'wo_type': 'cleaning',
                'user_id': client_id.user_id.id if client_id and client_id.user_id else False,
                'description': description,
            }

            # Crear la oportunidad
            new_lead = self.env['crm.lead'].create(lead_data)

            # Mensaje para notificación
            message = _(
                "Se ha creado una nueva oportunidad por incidente: %s") % new_lead.name

            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('OPORTUNIDAD CREADA'),
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