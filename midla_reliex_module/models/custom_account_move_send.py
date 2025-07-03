# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, modules, tools, Command


class CustomAccountMoveSend(models.TransientModel):
    _inherit = 'account.move.send'
    def _get_default_mail_partner_ids(self, move, mail_template, mail_lang):
        partners = super()._get_default_mail_partner_ids(move, mail_template, mail_lang)

        if move.partner_id and move.partner_id.invoice_email:
            # Buscar partner con el email definido en invoice_email
            custom_partner = move.partner_id
            partners.email = custom_partner.invoice_email  #piso con el mail de facturacion al destinatario

        return partners