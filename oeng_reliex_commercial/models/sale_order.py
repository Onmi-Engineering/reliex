from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    name = fields.Char()

    comments_notes = fields.Html('Observations to workers')
