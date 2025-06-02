from odoo import fields, models, api, _
from odoo.exceptions import UserError


class Incident(models.Model):
    _name = 'incident'
    _description = 'Incidents'
    _inherit = 'mail.thread'

    name = fields.Char('Name', default=lambda self: _('New'))
    name_description = fields.Char('Title')
    description = fields.Html('Description')
    state = fields.Selection([
        ('not_handling', 'No Handling'),
        ('handling', 'Handling'),
        ('finished', 'Handled'),
        ('unrealized', 'No realizado')
    ], default="not_handling", string="State")

    reason = fields.Char(string='Mótivo de no realización')

    incident_type = fields.Selection([
        ('customer_info', 'Customer Information'),
        ('reliex_info', 'Reliex Information'),
        
    ], string="Clase inf", required=True)

    incident_type2 = fields.Selection([
        ('accident', 'Siniestro'),
        ('quotation', 'Presupuesto'),
        ('not_realized', 'Trabajo no realizado'),
    ], string="Tipo")

    incident_type3 = fields.Selection([
        ('not_clean', 'No se ha limpiado motor'),
        ('not_worked', 'Trabajo no realizado'),
    ], string="Reason")

    incident_type4 = fields.Selection([
        ('client', 'Cliente'),
        ('reliex', 'Reliex'),
    ], string="Motivo")

    partner_id = fields.Many2one('res.partner', 'Client')
    establishment_id = fields.Many2one('res.partner', string='Establishment', compute='_compute_establishment_id', store=True)
    plant_id = fields.Many2one('res.partner', string='Plant')
    workorder_id = fields.Many2one('work.order.clean', string='Cleanning Work Order')
    workorder_plant_id = fields.Many2one('work.order.plant', string='Plant Work Order')
    worksheet_id = fields.Many2one('worksheet.part', string='Worksheet')

    @api.depends('plant_id')
    def _compute_establishment_id(self):
        for inc in self:
            if inc.plant_id:
                inc.write({'establishment_id': inc.plant_id.parent_id.id})
            else:
                inc.establishment_id = False

    def button_confirm(self):
        for rec in self:
            if rec.state == 'not_handling':
                rec.write({'state': 'handling'})
                if rec.incident_type == 'customer_info':
                    rec.write({'state': 'finished'})
                    # Agregado correo para customer_info
                    rec._send_incident_email()

                # Se debe crear un presupuesto
                if rec.incident_type2 == 'quotation':
                    if not rec.plant_id:
                        raise UserError(_('You have to indicate Worksheet part and plant in a incident in order to '
                                          'create a quotation of incidents.'))
                    stage_incident = self.env['crm.stage'].search([('incident', '=', True)])
                    client_id = rec.plant_id.parent_id.parent_id
                    description_incident = str(rec.worksheet_id.display_name or '') + ' | ' + str(
                        rec.name or '') + '\n' + str(rec.description or '')
                    lead_data = {
                        'name': _('Lead created by Incident'),
                        'partner_id': rec.plant_id.parent_id.id,
                        'plant_ids': (4, rec.plant_id.id),
                        'type': 'opportunity',
                        'stage_id': stage_incident.id,
                        'wo_type': 'cleaning',
                        'user_id': client_id.user_id.id,
                        'description': description_incident,
                        'created_by_incident': True,
                    }
                    self.env['crm.lead'].create(lead_data)
                    rec.write({'state': 'finished'})


    def button_reset(self):
        for rec in self:
            rec.write({'state': 'not_handling'})

    def button_finish(self):
        for rec in self:
            rec.write({'state': 'finished'})

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('incident') or _('New')
        return super().create(vals)

    def button_unrealized(self):
        for rec in self:
            if rec.state == 'not_handling':
                rec.write({'state': 'unrealized'})
            if rec.state == 'Handling':
                rec.write({'state': 'unrealized'})

    # Campo computado para verificar permisos
    plant_edit_permission = fields.Boolean(
        string='Permiso de edición de planta',
        compute='_compute_plant_edit_permission',
        store=False,
    )

    @api.depends_context('uid')
    def _compute_plant_edit_permission(self):
        """Determina si el usuario tiene permiso para editar el campo plant_id"""
        for record in self:
            # verifico si el usuario actual pertenece al grupo 'permisos_especiales'
            record.plant_edit_permission = self.user_has_groups('onmi_reliex_operations.onmi_group_permisos_especiales')


    def _send_incident_email(self):
        """ Creado para envíar correo electrónico con los documentos adjuntos del incidente"""
        for rec in self:
            if not rec.establishment_id or not rec.establishment_id.email:
                continue

            # Buscar el template de correo
            template = self.env.ref('onmi_reliex_operations.email_template_incident_notification', raise_if_not_found=False)
            if not template:
                continue

            # busco documentos adjuntos del incidente
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'incident'),
                ('res_id', '=', rec.id)
            ])

            # preparar lista de IDs de adjuntos
            attachment_ids = []
            if attachments:
                attachment_ids = attachments.ids

            try:
                template.send_mail(
                    rec.id,
                    email_values={
                        'email_to': rec.establishment_id.email,
                        'attachment_ids': [(6, 0, attachment_ids)] if attachment_ids else False
                    },
                    force_send=True
                )
            except Exception as e:
                import logging
                _logger = logging.getLogger(__name__)
                _logger.warning("Error sending incident email to %s: %s", rec.establishment_id.email, str(e))



