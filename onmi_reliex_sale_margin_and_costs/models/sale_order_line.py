from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    opportunity_id = fields.Many2one(
        "crm.lead", string="Opportunity", check_company=True,
        domain="[('type', '=', 'opportunity'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        compute="_compute_opportunity_id"
    )
    part_type = fields.Selection(related="order_id.part_type")
    cost = fields.Float(string='Cost')
    margin_percentage = fields.Float(string='Benefits (%)')
    margin_qty = fields.Float(string='Benefits')
    price_subtotal_without_margin = fields.Float("Subtotal without margin",
                                                 compute="_compute_price_subtotal_without_margin")
    subtotal_cost = fields.Float("Subtotal costs", compute="_compute_subtotal_cost")

    def _compute_subtotal_cost(self):
        for rec in self:
            rec.subtotal_cost = rec.cost * rec.product_uom_qty

    def _compute_price_subtotal_without_margin(self):
        for rec in self:
            rec.price_subtotal_without_margin = ((100 - rec.discount) / 100) * rec.price_unit * rec.product_uom_qty

    def _compute_opportunity_id(self):
        for rec in self:
            if rec.order_id:
                rec.opportunity_id = rec.order_id.opportunity_id

    # @api.onchange('margin_percentage')
    # def _onchange_price_unit(self):
    #     if self.margin_percentage > 0.0:
    #         self.price_unit = (1 + self.margin_percentage / 100) * self.cost
    #     else:
    #         self.price_unit = self.product_id.list_price

    def apply_margin(self):
        if self.cost == 0:
            raise UserError(_('you have to indicate cost to apply margin.'))
        else:
            self.price_unit = self.cost * (1+self.margin_percentage/100)
