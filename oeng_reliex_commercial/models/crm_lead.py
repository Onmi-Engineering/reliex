from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    extra_contact_ids = fields.One2many(
        'crm.lead.extra.contact',
        'lead_id',
        string='Contactos Adicionales'
    )
    extra_contact_count = fields.Integer(
        string='Número de Contactos Adicionales',
        compute='_compute_extra_contact_count'
    )

    @api.depends('extra_contact_ids')
    def _compute_extra_contact_count(self):
        for record in self:
            record.extra_contact_count = len(record.extra_contact_ids)

    def action_view_extra_contacts(self):
        """Acción para el botón inteligente"""
        return {
            'name': 'Contactos Adicionales',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead.extra.contact',
            'view_mode': 'tree,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
            'target': 'current',
        }
