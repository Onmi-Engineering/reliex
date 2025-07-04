from odoo import fields, models, api, _

class CustomWorkOrderClean(models.Model):
    _inherit = 'work.order.clean'

    def _get_attendee_emails_reports(self):
        self.ensure_one()
        emails = self.establishment_id.certif_email
        return emails

    def _get_attendee_emails_reports2(self):
        self.ensure_one()
        emails = self.establishment_id.certif_email
        return emails


    def _get_attendee_emails_confirmed(self):
        """ Get comma-separated attendee email addresses from sending reports WOC. """
        self.ensure_one()
        return self.establishment_id.stablish_email or ""

    def _get_attendee_emails_confirmed2(self):
        self.ensure_one()
        emails = self.establishment_id.stablish_email
        return emails

