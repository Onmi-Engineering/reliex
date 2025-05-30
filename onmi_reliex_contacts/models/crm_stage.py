from odoo import fields, models, api, _


class CrmStage(models.Model):
    _inherit = 'crm.stage'

    type = fields.Selection([('cleaning', 'Cleaning'), ('new_plant', 'New Plant')], 'WO Type')

    frecuency = fields.Boolean("By frecuency")
    incident = fields.Boolean("By indicent")
    doing_quotation = fields.Boolean("Doing Quotation")
