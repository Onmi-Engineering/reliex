# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.onchange('template_id')
    def on_change_template_id(self):
        for rec in self:
            model = self.env['ir.model'].sudo().search([('model', '=', 'work.order.clean')])
            if rec.template_id.model_id.id == model.id and rec.template_id.send_reports:
                # Preparando pdfs a añadir

                # 20/06/2024 Comento esta linea original ya que res_id no existe mas ahora es res_ids
                # domain = [('res_model', '=', 'work.order.clean'), ('res_id', '=', rec.res_id),
                #           ('mimetype', '=', 'application/pdf')]
                # y agrego  ('res_id', '=', rec.res_ids.strip('[]')), quitando los [] para que no de error
                domain = [('res_model', '=', 'work.order.clean'), ('res_id', '=', rec.res_ids.strip('[]')),
                          ('mimetype', '=', 'application/pdf')]
                attachment_to_assign = self.env['ir.attachment'].search(domain)
                rec.attachment_ids = attachment_to_assign


    def send_mail(self, auto_commit=False):
        followers_to_restore = self.env.context.get('followers_to_restore', [])
        work_order_id = self.env.context.get('work_order_id')

        result = super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)

        # Restauro seguidores usando metodo asíncrono
        if followers_to_restore and work_order_id:
            self.env['work.order.clean'].browse(work_order_id).with_delay()._restore_followers(followers_to_restore)

        return result