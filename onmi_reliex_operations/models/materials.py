from odoo import fields, models, api, _


class Materials(models.Model):
    _name = 'materials'
    _description = 'Materials from List of Materials'

    name = fields.Char('Name')
    id = fields.Char(string='Identifier', readonly=True)
    product_id = fields.Many2one('product.product', "Product", required=True)
    plant_id = fields.Many2one('res.partner')
    wo_clean_id = fields.Many2one('work.order.clean')
    wo_plant_id = fields.Many2one('work.order.plant')
    worksheet_id = fields.Many2one('worksheet.part')
    sale_order_id = fields.Many2one('sale.order')
    sale_order_line_id = fields.Many2one('sale.order.line')
    supplier_ids = fields.Many2many('res.partner', string='Suppliers')
    supplier_id = fields.Many2one('res.partner', string='Supplier')
    list_id = fields.Many2one('material.list')
    description_sale = fields.Text('Description', compute='_compute_description_sale')

    establishment_list = fields.Many2one('res.partner', related="list_id.establishment_id")

    quantity = fields.Float('Quotation Quantity')
    qty_to_prepair = fields.Float('Quantity to prepair')
    qty_on_stock = fields.Float('Quantity on stock', compute="_compute_qty_on_stock")
    qty_on_parts = fields.Float('Quantity being spent')
    order_date = fields.Datetime('Order date')
    delivery_date = fields.Datetime('Delivery date')
    material_preparation_done = fields.Boolean('Material preparation done')
    surplus_material = fields.Char('Surplus Material')
    qty_consumed = fields.Float('Units')
    location = fields.Selection([('place', 'On place'), ('storage', 'Storage')], 'Location')

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False)

    @api.depends('sale_order_line_id', 'product_id')
    def _compute_description_sale(self):
        for rec in self:
            if rec.sudo().sale_order_line_id:
                rec.sudo().write({'description_sale': rec.sudo().sale_order_line_id.name})
            elif rec.product_id:
                rec.sudo().write({'description_sale': rec.product_id.name})
                rec.description_sale = rec.product_id.name
            else:
                rec.sudo().write({'description_sale': ''})

    @api.onchange('quantity', 'qty_on_stock')
    def _on_change_qty_to_prepair(self):
        for rec in self:
            if not rec.id:
                rec.qty_to_prepair = 0
                continue
            if rec.quantity > 0.0:
                rec.qty_to_prepair = rec.quantity - rec.qty_on_stock
                if rec.qty_to_prepair < 0:
                    rec.qty_to_prepair = 0

    @api.onchange('product_id')
    def _compute_qty_on_stock(self):
        for rec in self:
            if not rec.id:
                rec.qty_on_stock = 0
                continue
            if rec.product_id:
                rec.qty_on_stock = rec.product_id.qty_available