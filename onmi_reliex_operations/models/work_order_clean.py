from odoo import fields, models, api, _
from odoo.exceptions import UserError
from bs4 import BeautifulSoup
import base64
import datetime
import html2text
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError


class CustomModel(models.Model):
    _name = 'custom.model'
    _description = 'Custom Model'

    work_order_clean_id = fields.Many2one('work.order.clean')

    selection_field = fields.Selection(
        [('assign', 'Asignar operarios'), ('proposed', 'Modificar fecha propuesta')],
        string='Campo de Selección',
        default='assign',
    )

    def safe_state(self):

        if self.work_order_clean_id:
            if self.selection_field == 'assign':
                self.work_order_clean_id.write({'state': 'assign'})
            if self.selection_field == 'proposed':
                self.work_order_clean_id.write({'state': 'proposed'})


class AcceptModel(models.Model):
    _name = 'accept.model'
    _description = 'Accept Model'

    work_order_clean_id = fields.Many2one('work.order.clean')

    selection_field = fields.Selection(
        [('assign', 'Asignar operarios'), ('proposed', 'Modificar fecha propuesta')],
        string='Campo de Selección',
        default='assign',
    )

    def safe_state(self):

        if self.work_order_clean_id:
            if self.selection_field == 'assign':
                self.work_order_clean_id.write({'state': 'assign'})
            if self.selection_field == 'proposed':
                self.work_order_clean_id.write({'state': 'proposed'})


class WorkOrdersClean(models.Model):
    _name = 'work.order.clean'
    _description = 'Cleanning Work Orders'
    _inherit = 'mail.thread'
    _rec_name = 'new_display_name'

    name = fields.Char(string='Reference of Work Order Clean', default=lambda self: _('New'))
    new_display_name = fields.Char('New display Name', compute="_compute_new_display_name")

    comments_notes = fields.Html('Comments Notes', compute="compute_comments_notes")
    complete_system = fields.Boolean('Complete system', tracking=True)
    boss_name = fields.Char('Gerente', related='establishment_id.boss_name')
    parent_id = fields.Many2one('res.partner', related='establishment_id.parent_id')
    supervisor_name = fields.Char('Supervisor', related='establishment_id.supervisor_name')
    supervisor_email = fields.Char('Supervisor email', related='establishment_id.supervisor_email')
    supervisor_phone = fields.Char('Supervisor phone', related='establishment_id.supervisor_phone')
    function = fields.Char('Puesto de trabajo', related='establishment_id.function')
    phone = fields.Char('Telefono', related='establishment_id.phone')
    email = fields.Char('Correo electrónico', related='establishment_id.email')
    mobile = fields.Char('Móvil', related='establishment_id.mobile')
    website = fields.Char('Sitio Web', related='establishment_id.website')
    category_id = fields.Many2many('res.partner.category', related='establishment_id.category_id')
    is_company = fields.Boolean(string='Is a Company', related='establishment_id.is_company')
    type = fields.Selection(related='partner_id.type')
    user_ids = fields.One2many('res.users', 'partner_id', string='Users', auto_join=True, readonly=True)
    street = fields.Char(related='establishment_id.street')
    street2 = fields.Char(related='establishment_id.street2', readonly=True)
    city = fields.Char(related='establishment_id.city')
    zip = fields.Char(related='establishment_id.zip')
    state_id = fields.Many2one('res.country.state', related='establishment_id.state_id')
    country_id = fields.Many2one('res.country', related='establishment_id.country_id')
    state = fields.Selection(string='Status', required=True, readonly=False, copy=False, tracking=True, selection=[
        ('to_plan', 'To Plan'),
        ('waiting', 'Esperando respuesta'),
        ('assign', 'Asignar Operarios'),
        ('proposed', 'Modificar fecha propuesta'),
        ('confirm', 'To Handl'),
        ('handled', 'In Process'),
        ('to_finish', 'To Finish'),
        ('finished', 'Finished'),
        ('invoiced', 'Invoiced'),
    ], default='to_plan',
                             help="The current state of your work order:\n"
                                  "\t- To Plan: Asign Work Orders data.\n"
                                  "\t- Planned: Waiting for Client confirmation and Worker notification.\n"
                                  "\t- Confirmed by Client: It is proceed to book hotels and access.\n"
                                  "\t- In Process: Fill daily worksheets.\n"
                                  "\t- To finish: Checked report information. Send reports.\n"
                                  "\t- Finished: Invoice is created and send to client.\n"
                                  "\t- Invoiced: Recieve receipt according to expiration.")

    start_date = fields.Datetime(string='Start date')
    description_date = fields.Char()
    end_date = fields.Datetime(string='End date')
    user_id = fields.Many2one('res.users', string='Boss Team')
    partner_id = fields.Many2one('res.partner', 'Client')
    establishment_id = fields.Many2one('res.partner', string='Establishment')
    plant_id = fields.Many2one('res.partner', string='Plant')
    related_plant_ids = fields.Many2many('res.partner', string='Related plants')
    lead_id = fields.Many2one('crm.lead', string='Lead')

    comments = fields.Text('Observations')

    worksheet_count = fields.Integer(compute='_compute_worksheet_count',
                                     string="Number of Worksheets")
    worksheetclean_count = fields.Integer(compute='_compute_worksheetclean_count',
                                          string="Number of WorksheetsCleans")

    incident_count = fields.Integer(compute='_compute_incident_count',
                                    string="Number of Incidents")
    pending_debts = fields.Boolean("Has pending debts", compute="_compute_pending_debts", store=False)
    line_ids = fields.One2many('work.order.line', 'wo_clean_id')
    worksheet_ids = fields.One2many('worksheet.part', 'workorder_id')

    access_url = fields.Char(related="establishment_id.access_url")

    access_notifications = fields.Html(related="establishment_id.access_notifications")

    employee_id = fields.Many2many('hr.employee', string='Employees')
    allday = fields.Boolean("Apply all day long", default=True)
    report_cleaning_comments = fields.Html('Observations on report cleaning')

    line_ids = fields.One2many('materials', 'wo_clean_id')

    activity_ids = fields.One2many('mail.activity', 'res_id', string='Activities')

    operators_notified = fields.Boolean('Operators Notified')

    invoice_created = fields.Boolean('Invoice created')
    report_sent = fields.Boolean('Reports sent')

    # complete_system = fields.Boolean('Complete system', tracking=True)
    cooker_hood = fields.Boolean('Cooker hood')
    duct = fields.Boolean('Duct')
    extractor = fields.Boolean('Extractor')
    filtronic = fields.Boolean('Filtronic')
    make_visible = fields.Boolean(string="User", compute="get_user", default=True)
    access_check = fields.Boolean(string='Acceso documental', related='establishment_id.access_check',
                                  help="Si el Check está True la otl pasára a estado(para tramitar), si es False a (en proceso)")
    accepted_date = fields.Datetime(string='Fecha aceptación')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'work.order.clean')],
                                     string='Attachments')
    work_notes = fields.Html('Work notes', related="lead_id.work_notes")

    alert_establishment_related = fields.Html(
        string='Alerta',
        related='establishment_id.alert_establishment',
        readonly=True
    )

    monitor = fields.Many2one(
        'res.users',
        string='Monitor',
        domain=lambda self: [('groups_id', 'in', [self.env.ref('onmi_reliex_operations.group_monitor_manager').id])]
    )
    # # # # # # # # # # # # PARA MOSTRAR DEUDA DE CLIENTE# # # # # # # # # # # # # # # v
    # total_debt = fields.Monetary(
    #     string='Total Deuda',
    #     currency_field='currency_id',
    #     readonly=True
    # )
    total_debt = fields.Monetary(
        string='Total Deuda',
        currency_field='currency_id',
        compute='_compute_total_debt',
        store=True  # Opcional: para guardar en BD y mejorar performance
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id
    )
    # # # # # # # # # # # # PARA MOSTRAR DEUDA DE CLIENTE# # # # # # # # # # # # # # # v



    def write(self, values):
        old_start_date = self.start_date
        result = super(WorkOrdersClean, self).write(values)

        if 'start_date' in values and values['start_date'] != old_start_date:
            for rec in self:
                if rec.start_date:
                    date_asign = rec.start_date
                    for worksheet in rec.worksheet_ids:
                        if worksheet.id != rec.worksheet_ids[0].id:
                            date_asign = date_asign + timedelta(days=1)
                        # if date_asign.weekday() == 5:
                        #     date_asign = date_asign + timedelta(days=2)
                        # if date_asign.weekday() == 6:
                        #     date_asign = date_asign + timedelta(days=1)
                        worksheet.start_date = date_asign
        return result

        # if work_id.worksheet_ids:
        #     idx = 0
        #     worksheet_idx = 0

        #     while worksheet_idx < len(work_id.worksheet_ids):
        #         current_date = self.start_date + timedelta(days=idx)
        #         if current_date.weekday() not in [5, 6]:
        #             work_id.worksheet_ids[worksheet_idx].start_date = current_date
        #             worksheet_idx += 1
        #         idx += 1

    # @api.depends("start_date")
    # def calcule_date_part(self):
    #       work_id = self.env['work.order.clean'].search([('id', '=', self.ids[0])])
    #       if work_id.worksheet_ids:
    #           idx = 0 
    #           worksheet_idx = 0

    #           while worksheet_idx < len(work_id.worksheet_ids):
    #             current_date = self.start_date + timedelta(days=idx)
    #             if current_date.weekday() not in [5, 6]:
    #                 work_id.worksheet_ids[worksheet_idx].start_date = current_date
    #                 worksheet_idx += 1
    #             idx += 1
    #             work_id.write({
    #             'worksheet_ids': [(6, 0, work_id.worksheet_ids.ids)]  
    #         })                             

    def action_reschedule(self):
        for rec in self:
            if rec.state == 'reschedule':
                rec.write({'state': 'assign'})

    def action_accepted(self):
        for rec in self:
            if rec.state == 'accepted':
                rec.write({'state': 'confirm'})

    def action_open_popup(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Seleccionar Estado',
            'res_model': 'accept.model',
            'view_mode': 'form',
            # 'view_id': self.env.ref('custom_model.view_custom_model_form').id,
            'target': 'new',
            'context': {
            'default_work_order_clean_id': self.id,
            },
        }

    def action_open_waiting_popup(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Seleccionar Estado',
            'res_model': 'custom.model',
            'view_mode': 'form',
            # 'view_id': self.env.ref('custom_model.view_custom_model_form').id,
            'target': 'new',
            'context': {
                'default_work_order_clean_id': self.id,
            },
        }

    def get_user(self):
        active_user_id = self.env.user.id
        active_user = self.env['res.users'].search([('id', '=', active_user_id)])
        for x in self:
            if active_user.env.user.has_group('onmi_reliex_operations.otl_editable'):
                x.make_visible = True
            else:
                x.make_visible = False

    def _compute_worksheetclean_count(self):
        for rec in self:
            rec.worksheetclean_count = 0
            worksheets = self.env['work.order.clean'].search_count(
                [('establishment_id', '=', self.establishment_id.id)])

            if worksheets:
                rec.worksheetclean_count = worksheets

    def compute_comments_notes(self):
        for rec in self:
            establishment_text = _(
                f"<b>Establecimiento:</b><br/>{rec.establishment_id.comment}<br/>")
            child_comments = "<br/><b>Instalaciones:</b><br/>"
            for plant in rec.related_plant_ids:
                if plant.comment:
                    child_comments += _(f"&nbsp;<b>Instalación {plant.name}:</b><p>{plant.comment}</p>")

            rec.comments_notes = "<p>" + establishment_text + child_comments + "</p>"

    @api.onchange('user_id', 'employee_id')
    def _change_worksheet_user_and_employees(self):
        for rec in self:
            woc = self.env['work.order.clean'].search([('id', '=', rec.id.origin)])
            if woc.user_id and woc.worksheet_ids:
                woc.worksheet_ids.user_id = rec.user_id
            if rec.employee_id and woc.worksheet_ids:
                woc.worksheet_ids.employee_id = rec.employee_id

    def _compute_pending_debts(self):
        for rec in self:
            if rec.establishment_id:
                account = self.env['account.account'].search([('code', '=', '430000')])
                rec.pending_debts = False
                lines = self.env['account.move.line'].search([('display_type', 'not in', ('line_section', 'line_note')),
                                                              ('partner_id', '=', rec.establishment_id.parent_id.id),
                                                              ('parent_state', '=', 'posted'),
                                                              ('account_id', 'in', account.ids)])
                balance = 0
                for l in lines:
                    balance += l.debit - l.credit
                if round(balance, 2) < 0:
                    rec.pending_debts = True
                else:
                    rec.pending_debts = False

    def action_client_confirmed(self):
        for rec in self:
            if rec.state == 'assign' and rec.access_check == True:
                rec.write({'state': 'confirm'})
            else:
                rec.write({'state': 'handled'})

    def action_handled(self):
        for rec in self:
            if rec.state == 'confirm':
                rec.write({'state': 'handled'})

    def action_to_finish(self):
        for rec in self:
            if rec.state == 'handled':
                rec.write({'state': 'to_finish'})

    def action_finished(self):
        for rec in self:
            if rec.state == 'to_finish':
                worksheets = self.env['worksheet.part'].search([('workorder_id.id', '=', self.id)])
                worksheets_checked = worksheets.filtered(lambda w: w.state == 'done_and_check')
                if len(worksheets) == len(worksheets_checked):
                    rec.write({'state': 'finished'})
                    rec.end_date = datetime.datetime.now()
                else:
                    raise UserError(_('You have to check all the parts related with this Work Order'))

    def action_invoiced(self):
        for rec in self:
            if rec.state == 'finished':
                rec.write({'state': 'invoiced'})

    def action_reset(self):
        for rec in self:
            rec.write({'state': 'to_plan'})

    def send_mail_success_callback(self):
        self.write({'state': 'planned'})

    def action_send_by_mail(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()

        # COMIENZO CONTROL AGREGADO 20/06/2024
        # Por la migracion el campo start_date_tz no tiene valor y da error en esta funcion
        # Agrego condicion para verificar si el modelo worksheet.part tiene el campo start_date_tz vacío
        # y agrego mensaje para que redifina el campo Fecha inicio
        for worksheet in self.worksheet_ids:
            if not worksheet.start_date_tz:
                raise UserError("Por favor, redefina la fecha de inicio para continuar.")
        # FINN CONTROL AGREGADO

        template_id = self.env.ref('onmi_reliex_reports.onmi_mail_template_workorder_clean_confirm_document4').id
        lang = self.env.context.get('lang')
        template = self.env.ref('onmi_reliex_reports.onmi_mail_template_workorder_clean_confirm_document4')
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]

        # Para borrar seguidores al enviar correo, luego restaura mas abajo
        current_followers = self.message_partner_ids.ids
        if current_followers:
            self.message_unsubscribe(current_followers)


        ctx = {
            'default_model': 'work.order.clean',
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'model_description': self._description,
            # Para que no envie a seguidores
            'followers_to_restore': current_followers,
            'work_order_id': self.id,  # Pasar el ID del registro

        }

        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

        if action:
            self.write({'state': 'waiting'})
            return action

    def action_confirm_by_mail(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        if not self.employee_id:
            raise UserError("Debe indicar los operarios primero.")
        self.ensure_one()
        template_id = self.env.ref('onmi_reliex_reports.onmi_mail_template_workorder_reports_confirm23').id
        lang = self.env.context.get('lang')
        template = self.env.ref('onmi_reliex_reports.onmi_mail_template_workorder_reports_confirm23')
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'work.order.clean',
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'model_description': self._description,
        }
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
        if action:
            if self.state == 'assign' and self.access_check == True:
                self.write({'state': 'handled'})
            else:
                self.write({'state': 'confirm'})

        return action

    def action_create_invoice(self):
        for rec in self:
            for so in rec.lead_id.order_ids:
                if not so.invoice_ids:
                    so._create_invoices()
                    rec.invoice_created = True
                else:
                    raise UserError(_('You have created an invoice yet.'))

    def action_generate_attachment(self):
        """ this method called from button action in view xml """
        REPORT_ID = 'onmi_reliex_reports.action_report_certifieds_work_order_clean'
        # Metodo nuevo para llamar a _render_qweb_pdf en V17
        pdf = self.env['ir.actions.report']._render_qweb_pdf(REPORT_ID, self.ids)[0]
        # Metodo deprecado para llamar a _render_qweb_pdf
        # pdf = self.env.ref(REPORT_ID)._render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf)
        ATTACHMENT_NAME = _('Certifieds' + '/' + self.name[0] + '.pdf')
        self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'store_fname': ATTACHMENT_NAME,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

        REPORT_ID = 'onmi_reliex_reports.action_report_work_order_clean'
        pdf = self.env['ir.actions.report']._render_qweb_pdf(REPORT_ID,self.ids)[0]
        b64_pdf = base64.b64encode(pdf)
        ATTACHMENT_NAME = _('Report' + '/' + self.name[0] + '.pdf')
        self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'store_fname': ATTACHMENT_NAME,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

    def action_send_reports(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        domain = [('mimetype', '=', 'application/pdf'), ('res_model', '=', self._name)]
        self.env['ir.attachment'].search(domain).unlink()
        self.action_generate_attachment()
        template_id = self.env.ref('onmi_reliex_reports.onmi_mail_template_workorder_reports_document').id
        lang = self.env.context.get('lang')
        template = self.env.ref('onmi_reliex_reports.onmi_mail_template_workorder_reports_document')
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]

        current_followers = self.message_partner_ids.ids

        if current_followers:
            self.message_unsubscribe(current_followers)
            print(f"Seguidores eliminados: {current_followers}")
        ctx = {
            'default_model': 'work.order.clean',
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'model_description': self._description,
            'followers_to_restore': current_followers,
            'work_order_id': self.id,
        }
        self.report_sent = True
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def _compute_new_display_name(self):
        for rec in self:
            rec.new_display_name = rec.name
            if rec.partner_id:
                rec.new_display_name = rec.name + " - " + rec.partner_id.name
                if rec.establishment_id:
                    rec.new_display_name = rec.name + " - " + rec.establishment_id.name
                    if rec.establishment_id.city:
                        rec.new_display_name = rec.name + " - " + rec.establishment_id.name + " - " + rec.establishment_id.city

    def _compute_incident_count(self):
        for rec in self:
            rec.incident_count = 0
            incidents = self.env['incident'].search_count(
                [('worksheet_id.workorder_id.id', '=', self.id)])
            if incidents > 0:
                rec.incident_count = incidents

    def _compute_worksheet_count(self):
        for rec in self:
            rec.worksheet_count = 0
            worksheets = self.env['worksheet.part'].search_count([('workorder_id', '=', rec.id)])
            if worksheets:
                rec.worksheet_count = worksheets

    def action_worksheet_new(self):
        ctx = {
            'default_partner_id': self.partner_id.id,
            'default_establishment_id': self.establishment_id.id,
            'default_workorder_id': self.id,
            'default_part_type': 'cleaning',
            'default_user_id': self.user_id.id,
        }
        return {
            'name': _('Create Worksheet'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'worksheet.part',
            'view_id': self.env.ref('onmi_reliex_operations.worksheet_form_view').id,
            'context': ctx,
        }

    def action_view_incident(self):
        action = self.env["ir.actions.actions"]._for_xml_id("onmi_reliex_operations.onmi_action_incident")
        action['domain'] = [('worksheet_id.workorder_id.id', '=', self.id)]
        return action

    def action_view_worksheet(self):
        action = self.env["ir.actions.actions"]._for_xml_id("onmi_reliex_operations.onmi_action_worksheet")
        action['domain'] = [('workorder_id.id', '=', self.id)]
        action['context'] = {}
        return action

    def action_view_worksheetclean(self):

        works = self.env['work.order.clean'].search([('establishment_id', '=', self.establishment_id.id)])
        action = self.env["ir.actions.actions"]._for_xml_id("onmi_reliex_operations.onmi_action_work_order_clean_full")
        action['domain'] = [('id', 'in', works.ids)]
        return action

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val.get('name') == _('New') or val.get('name') == 'New':
                val['name'] = self.env['ir.sequence'].next_by_code('work.order.clean')
        return super().create(vals)

    def action_recurring_by_mail(self):

        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self.env.ref('onmi_reliex_reports.onmi_mail_template_recurring_mail8').id
        lang = self.env.context.get('lang')
        template = self.env.ref('onmi_reliex_reports.onmi_mail_template_recurring_mail8')
        if template.lang:
            for part in self.worksheet_ids:
                lang = template._render_lang(part[0].ids)[part[0].id]
        ctx = {
            'default_model': 'work.order.clean',
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'model_description': self._description,
        }
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

        return action

    def recurring_mail1(self):

        prog = self.env['work.order.clean'].sudo().search([('state', 'in', ["handled", "assign", "confirm"])])
        for rec in prog:
            change_date_str = rec.start_date
            if change_date_str:
                last_redeemed_date = change_date_str.date()
                today = fields.Date.today()
                ays_until_start_date = (last_redeemed_date - today).days
                if ays_until_start_date == -1:
                    template_id = self.env.ref('onmi_reliex_reports.onmi_mail_template_recurring_mail').id
                    if template_id:
                        template = self.env['mail.template'].browse(template_id)
                    if template:
                        template.send_mail(rec.id, force_send=True)
                        message_body = f"Correo Recurrente enviado a {rec.establishment_id.email}"
                        rec.message_post(body=message_body, subject='Recordatorio de limpieza 24h antes del servicio.')
        return True

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('work.order.clean') or _('New')
        return super().create(vals)


    # Se agrega para dar aviso si desmarcan esta casilla ya que se utiliza para genera la oportunidad de frecuencia en CRM
    @api.onchange('complete_system')
    def _onchange_complete_system(self):
        if self._origin.complete_system != self.complete_system:  # Solo si realmente cambió
            if self.complete_system:
                message = ('ADVERTENCIA: Está activando el sistema completo. '
                           'Asegúrese de que esta acción es necesaria. Al hacerlo se generará una oportunidad de frecuencia')
            else:
                message = ('ADVERTENCIA: Está desactivando el sistema completo. '
                           'Asegúrese de que esta acción es necesaria. Al hacerlo NO se generará una oportunidad de frecuencia')

            return {
                'warning': {
                    'title': 'ATENCIÓN!!!!',
                    'message': message
                }
            }

    # # # # # # # # # # # # PARA MOSTRAR DEUDA DE CLIENTE# # # # # # # # # # # # # # #
    @api.depends('partner_id')
    def _compute_total_debt(self):
        for record in self:
            if record.partner_id:
                # Buscar facturas no pagadas
                domain = [
                    ('partner_id', '=', record.partner_id.id),
                    ('move_type', 'in', ['out_invoice', 'out_refund']),
                    ('state', '=', 'posted'),
                    ('payment_state', 'in', ['not_paid', 'in_payment', 'partial'])
                ]

                unpaid_invoices = self.env['account.move'].search(domain)
                record.total_debt = sum(unpaid_invoices.mapped('amount_total_signed'))
            else:
                record.total_debt = 0.0

    def action_show_customer_debt(self):
        """Acción para mostrar las facturas pendientes del cliente"""
        if not self.partner_id:
            raise UserError("Debe seleccionar un cliente primero.")

        if self.total_debt == 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Sin Deuda',
                    'message': f'El cliente {self.partner_id.name} no tiene deuda pendiente.',
                    'type': 'success',
                    'sticky': False,
                }
            }

        # Dominio para las facturas
        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ['not_paid', 'in_payment', 'partial'])
        ]

        return {
            'type': 'ir.actions.act_window',
            'name': f'Deuda de {self.partner_id.name}',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {
                'default_partner_id': self.partner_id.id,
                'search_default_group_by_partner': 1,
            },
            'target': 'current',
        }
    # # # # # # # # # # # # FIN PARA MOSTRAR DEUDA DE CLIENTE# # # # # # # # # # # # # # # v

    def _restore_followers(self, follower_ids):
        """Restaurar seguidores de forma asíncrona"""
        try:
            self.message_subscribe(follower_ids)
            print(f"Seguidores restaurados: {follower_ids}")
        except Exception as e:
            print(f"Error restaurando seguidores: {e}")
