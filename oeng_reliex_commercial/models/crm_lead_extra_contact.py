from odoo import models, fields, api

class CrmLeadExtraContact(models.Model):
    _name = 'crm.lead.extra.contact'
    _description = 'Contactos Adicionales del Lead'
    _order = 'sequence, id'

    lead_id = fields.Many2one('crm.lead', string='Lead', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Secuencia', default=10)
    extra_contact_name = fields.Char(string='Nombre del Contacto', required=True)
    extra_contact_function = fields.Char(string='Puesto de trabajo')
    extra_contact_mobile = fields.Char(string='Móvil')
    active = fields.Boolean(string='Activo', default=True)