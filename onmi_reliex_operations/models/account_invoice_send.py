from odoo import api, fields, models, Command, _


class AccountInvoiceSend(models.TransientModel):
    _inherit = 'account.invoice.send'

    def send_and_print_action(self):
        res = super().send_and_print_action()
        invoice = self.env['account.move'].search([('id', '=', self.res_id)])
        so = self.env['sale.order'].search([('invoice_ids', '=', invoice.id)])
        if so:
            lead = so.opportunity_id
            if lead:
                workorder = self.env['work.order.clean'].search([('lead_id', '=', lead.id)])
                if workorder:
                    workorder.action_invoiced()
        return res
