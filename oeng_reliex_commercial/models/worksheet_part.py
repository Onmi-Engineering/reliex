from odoo import fields, models, api


class Worksheet_Part(models.Model):
    _inherit = 'worksheet.part'

    def action_checked(self):
        super(Worksheet_Part, self).action_checked()
        for rec in self:
            for line in rec.cleaning_line_ids:
                for cooker in rec.plant_id.cooker_hood_ids:
                    if line.product_id.id in cooker.duct_register_ids.product_id.ids:
                        duct_register_line = cooker.duct_register_ids.filtered(lambda l: l.product_id.id == line.product_id.id)
                        self.env['duct.register'].create({
                            'cooker_id': duct_register_line.cooker_id.id,
                            'product_id': line.product_id.id,
                            'qty': -line.qty_consumed,
                            'worksheet_id': rec.id,
                        })
