from odoo import api, fields, models, modules


class Users(models.Model):
    _inherit = "res.users"

    monitor = fields.Boolean(string="Monitor")

