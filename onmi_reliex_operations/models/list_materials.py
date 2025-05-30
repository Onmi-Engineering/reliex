from odoo import fields, models, api, _

from odoo.exceptions import UserError


class MaterialList(models.Model):
    _name = 'material.list'
    _description = 'List of Materials'

    name = fields.Char('Name', default=_('New'))
    establishment_id = fields.Many2one('res.partner')
    lead_id = fields.Many2one('crm.lead')
    supplier_ids = fields.Many2many('res.partner', string="Suppliers")

    workorder_plant_id = fields.Many2one('work.order.plant')
    workorder_clean_id = fields.Many2one('work.order.clean')

    material_ids = fields.One2many('materials', 'list_id')

    def action_view_purchase_orders(self):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        action['domain'] = [('opportunity_id', '=', self.lead_id.id)]
        return action

    def action_create_purchase_orders(self):
        for rec in self:
            suppliers = rec.material_ids.supplier_ids
            for supplier in suppliers:
                purchase_vals = {
                    'partner_id': supplier.id,
                    'opportunity_id': rec.lead_id.id,
                    'origin': rec.lead_id.name
                }
                if supplier.property_supplier_payment_term_id:
                    purchase_vals['payment_term_id'] = supplier.property_supplier_payment_term_id.id
                if supplier.property_account_position_id:
                    purchase_vals['fiscal_position_id'] = supplier.property_account_position_id.id
                po = self.env['purchase.order'].create(purchase_vals)
                for material in rec.material_ids:
                    if supplier in material.supplier_ids:
                        po.write({'order_line': [(0, 0,
                                                  {'product_id': material.product_id.id,
                                                   'order_id': po.id,
                                                   'product_qty': material.quantity,
                                                   'price_unit': 0.0,
                                                   })]})
        return self.action_view_purchase_orders()

    def action_create_sale_order(self):
        for rec in self:
            plants = rec.lead_id.plant_ids
            if not plants:
                raise UserError(_('You have to indicate plants on opportunity.'))
            lines = rec.material_ids

            so = self.env['sale.order'].create({
                'partner_id': rec.establishment_id.id,
                'opportunity_id': rec.lead_id.id,
                'origin': rec.lead_id.name,
                'payment_term_id': rec.establishment_id.parent_id.property_payment_term_id.id,
            })
            for plant in plants:
                so.write({'order_line': [(0, 0,
                                          {'name': plant.name,
                                           'display_type': 'line_section'
                                           })]})
                for line in lines:
                    if line.plant_id.id == plant.id:
                        so.write({'order_line': [(0, 0,
                                                  {'product_id': line.product_id.id,
                                                   'order_id': so.id,
                                                   'product_uom_qty': line.quantity,
                                                   })]})

            rec.lead_id.stage_id = self.env['crm.stage'].search(
                [('type', '=', 'new_plant'), ('doing_quotation', '=', True)], limit=1)

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val.get('name') == _('New') or val.get('name') == 'New':
                val['name'] = self.env['ir.sequence'].next_by_code('material.list')
        return super().create(vals)
