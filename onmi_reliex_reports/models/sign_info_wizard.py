from odoo import fields, models, api


class SignInfoWizard(models.TransientModel):
    _inherit = 'sign.info.wizard'

    def confirm_sign_and_send(self):
        super().confirm_sign_and_send()
        return self.worksheet_id.action_worksheet_send()
