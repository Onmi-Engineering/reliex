from odoo import fields, models, api


class DuctRegister(models.Model):
    _name = 'duct.register'

    product_id = fields.Many2one('product.product')
    qty = fields.Float('Qty')
    cooker_id = fields.Many2one('cooker.hood')
    plant_id = fields.Many2one('res.partner')
    worksheet_id = fields.Many2one('worksheet.part')
    worksheet_name = fields.Char(related='worksheet_id.name')
