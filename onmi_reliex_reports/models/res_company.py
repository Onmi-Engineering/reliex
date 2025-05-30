from odoo import fields, models, api


class ModelName(models.Model):
    _inherit = 'res.company'
    _description = 'Description'

    signature_leader = fields.Binary('Signature leader')
