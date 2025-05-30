import datetime

from odoo import fields, models, api
import datetime
from pytz import timezone
import pytz


class WorksheetPart(models.Model):
    _inherit = 'worksheet.part'

    next_frecuency_date = fields.Datetime('Next frecuency date', compute="_compute_next_frecuency_date", store=False)

    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'worksheet.part')],
                                     string='Attachments')

    start_date_tz = fields.Datetime(string='Start date with TZ', compute='_compute_start_date_tz')

    @api.depends('start_date')
    def _compute_start_date_tz(self):
        for record in self:
            if record.start_date:
                user_tz = self.env.user.tz or 'UTC'
                local_tz = timezone(user_tz)
                fecha_con_tz = pytz.UTC.localize(record.start_date).astimezone(local_tz)
                record.start_date_tz = fecha_con_tz.strftime('%Y-%m-%d %H:%M:%S')
            else:
                record.start_date_tz = False

    def _compute_next_frecuency_date(self):
        for rec in self:
            if rec.start_date and rec.establishment_id.frecuency_active:
                rec.next_frecuency_date = rec.start_date + datetime.timedelta(days=rec.establishment_id.delay)

    def _get_attendee_emails_workers(self):
        """ Get comma-separated attendee email addresses from sending notification from workers. """
        self.ensure_one()
        emails = ""
        if self.user_id.login:
            emails += self.user_id.login
        if self.employee_id:
            for op in self.employee_id:
                if op.work_email:
                    emails += "," + op.work_email
        return emails

    def _get_email_to_document_signed(self):
        """ Get comma-separated attendee email addresses from sending notification from workers. """
        self.ensure_one()
        emails = ""
        if self.establishment_id.email:
            emails += self.establishment_id.email
        if self.establishment_id.parent_id.email:
            emails += "," + self.establishment_id.parent_id.email
        if self.plant_id.email:
            emails += "," + self.plant_id.email
        if self.user_id.login:
            emails += "," + self.user_id.login
        return emails

    def action_worksheet_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self.env.ref('onmi_reliex_reports.onmi_mail_template_worksheet_signed_document').id
        lang = self.env.context.get('lang')
        template = self.env.ref('onmi_reliex_reports.onmi_mail_template_worksheet_signed_document')
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'worksheet.part',
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'model_description': self._description,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def action_worksheet_notify_workers(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self.env.ref('onmi_reliex_reports.onmi_mail_template_worksheet_clean_assign_work').id
        lang = self.env.context.get('lang')
        template = self.env.ref('onmi_reliex_reports.onmi_mail_template_worksheet_clean_assign_work')
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'worksheet.part',
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'model_description': self._description,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

