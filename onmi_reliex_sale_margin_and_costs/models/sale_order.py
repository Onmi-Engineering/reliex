from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    part_type = fields.Selection(related="opportunity_id.wo_type")

    benefits = fields.Float('Benefits')
    benefits_percent = fields.Float('Benefits %')
    costs = fields.Float('Costs')
    commercial_margin = fields.Float('Commercial Margin (%)')
    commercial_margin_qty = fields.Float('Commercial Margin')
    cm_applied = fields.Boolean('CM Applied', default=False)
    cm_reset = fields.Boolean('CM Reset', default=True)

    def update_line_values(self):
        for rec in self:
            for line in rec.order_line:
                if line.price_subtotal_without_margin and line.cost and line.product_uom_qty:
                    line.margin_qty = line.price_subtotal_without_margin - line.cost * line.product_uom_qty
                if line.margin_qty and line.price_subtotal_without_margin:
                    line.margin_percentage = (line.margin_qty / line.price_subtotal_without_margin) * 100
            rec.update_benefits_and_costs()

    def apply_commercial_margin(self):
        for rec in self:
            comercial_margin_qty = 0
            for line in rec.order_line:
                comercial_margin_qty += line.price_subtotal_without_margin
            rec.commercial_margin_qty = comercial_margin_qty* rec.commercial_margin/100
            for line in rec.order_line:
                line.price_unit = line.price_unit * (100 + rec.commercial_margin) / 100
            rec.cm_applied = True
            rec.cm_reset = False

    def reset_commercial_margin(self):
        for rec in self:

            for line in rec.order_line:
                reset_price_unit = line.price_unit / (1+(rec.commercial_margin/100))
                line.price_unit = reset_price_unit
            rec.commercial_margin = 0.0
            rec.commercial_margin_qty = 0.0
            rec.cm_applied = False
            rec.cm_reset = True

    def update_benefits_and_costs(self):
        for rec in self:
            rec.benefits = 0.0
            total_cost = 0.0
            total_price = 0.0
            total_benefits = 0.0
            for line in rec.order_line:
                total_cost += line.cost * line.product_uom_qty
                total_price += line.price_subtotal_without_margin
                total_benefits += line.margin_qty
            rec.costs = total_cost
            rec.benefits = total_benefits
            rec.benefits_percent = ((total_price - total_cost) / total_price) * 100
