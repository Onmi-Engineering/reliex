from odoo import fields, models, api, _

class CustomWorkOrderClean(models.Model):
    _inherit = 'work.order.clean'

    def _get_attendee_emails_reports2(self):
        self.ensure_one()
        emails = self.partner_id.certif_email
        return emails

    def _get_attendee_emails_confirmed2(self):
        self.ensure_one()
        emails = self.partner_id.stablish_email
        return emails