from odoo import models

class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    def action_transfer_to_cash(self):
        return {
            'name': 'Traspasar a Efectivo',
            'type': 'ir.actions.act_window',
            'res_model': 'bank.to.cash.transfer.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }
