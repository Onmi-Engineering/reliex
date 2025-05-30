from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_system_complete = fields.Boolean(string='Sistema completo')
