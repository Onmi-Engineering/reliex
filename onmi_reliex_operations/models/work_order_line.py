from odoo import fields, models, api, _


class WorkOrderLine(models.Model):
    _name = 'work.order.line'
    _description = 'Lines of Work Orders'

    name = fields.Char('Name')
    id = fields.Char(string='Identifier (WO lines)', readonly=True)
    product_id = fields.Many2one('product.product', "Product", required=True)
    wo_clean_id = fields.Many2one('work.order.clean')
    wo_plant_id = fields.Many2one('work.order.plant')

    quantity = fields.Float('Quotation Quantity')
    qty_to_prepair = fields.Float('Quantity to prepair')
    qty_on_stock = fields.Float('Quantity on stock')
    supplier_id = fields.Many2one('res.partner', string='Supplier')
    order_date = fields.Datetime('Order date')
    delivery_date = fields.Datetime('Delivery date')
    material_preparation_done = fields.Boolean('Material preparation done')