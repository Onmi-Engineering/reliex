from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    material_ids = fields.Many2many('materials', 'sale_order_id', string='Materials')
    supplier_ids = fields.Many2many('res.partner', string='Suppliers')

    opportunity_wo_type = fields.Selection([('cleaning', 'Cleaning'), ('new_plant', 'New Plant')])


