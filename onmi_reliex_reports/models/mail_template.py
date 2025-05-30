from odoo import fields, models, api


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    send_reports = fields.Boolean('Send reports')
    can_write = fields.Boolean('Can Write', default=True)
