from odoo import fields, models, api, _


class HumanResources(models.Model):
    _name = 'human.resources'
    _description = 'Human resources'

    name = fields.Char('Name')
    id = fields.Char(string='Identifier', readonly=True)
    product_id = fields.Many2one('product.product', "Product", required=True)
    plant_id = fields.Many2one('res.partner')
    wo_clean_id = fields.Many2one('work.order.clean')
    wo_plant_id = fields.Many2one('work.order.plant')
    worksheet_id = fields.Many2one('worksheet.part')
    sale_order_id = fields.Many2one('sale.order')

    quantity = fields.Float('Units')
