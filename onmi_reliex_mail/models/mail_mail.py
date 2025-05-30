from odoo import models, _
from odoo.exceptions import UserError


class MailMail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False):
        max_total_size = 20 * 1024 * 1024  # 10MB

        for mail in self:
            total_size = sum(attachment.file_size for attachment in mail.attachment_ids)

            if total_size > max_total_size:
                raise UserError(_("Unable to send mail: total size of attachments exceeds 20 MB."))

        return super(MailMail, self).send(auto_commit=auto_commit, raise_exception=raise_exception)