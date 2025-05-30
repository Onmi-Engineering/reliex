from odoo import fields, models, api


class MaterialList(models.Model):
    _inherit = 'material.list'

    def action_create_sale_order(self):
        super(MaterialList, self).action_create_sale_order()
        for rec in self:
            so = self.env['sale.order'].search(
                [('partner_id', '=', rec.establishment_id.id), ('opportunity_id', '=', rec.lead_id.id),
                 ('origin', '=', rec.lead_id.name)])
            sale_lines = so.order_line
            po = self.env['purchase.order'].search([('opportunity_id', '=', rec.lead_id.id)])
            if po:
                for sl in sale_lines:
                    purchase_lines = po.order_line.filtered(lambda ol: ol.product_id.id == sl.product_id.id)
                    if purchase_lines:
                        max_cost = max(purchase_lines.mapped('price_unit'))
                        sl.cost = max_cost
                    else:
                        sl.cost = 0.0
