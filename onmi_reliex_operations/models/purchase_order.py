from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    po_selected = fields.Boolean('Purchase Order selected')

    opportunity_id = fields.Many2one('crm.lead')
