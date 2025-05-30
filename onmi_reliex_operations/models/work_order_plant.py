from odoo import fields, models, api, _
from odoo.exceptions import UserError
import datetime


class WorkOrderPlant(models.Model):
    _name = 'work.order.plant'
    _description = 'Work order Plant'
    _inherit = 'mail.thread'

    name = fields.Char(string='Reference of Work Order Plant', default=lambda self: _('New'))

    state = fields.Selection(string='Status.', required=True, readonly=False, copy=False, tracking=True, selection=[
        ('to_plan', 'To Plan'),
        ('to_hand', 'To Handle'),
        ('in_process', 'In Process'),
        ('finished', 'Finished'),
        ('invoiced', 'Invoiced'),
    ], default='to_plan',
                             help="The current state of your work order:\n"
                                  "\t- To Plan: Waiting for Purchase order confirmed.\n"
                                  "\t- To Handle: Asign Work Orders data.\n"
                                  "\t- In Process: It is proceed to book hotels and access.\n"
                                  "\t- Finished: Invoice is created and send to client.\n"
                                  "\t- Invoiced: Receive receipt according to expiration.")

    start_date = fields.Datetime(string='Start date')
    end_date = fields.Datetime(string='End date', compute='_compute_end_date')
    duration = fields.Float(string='Duration')
    user_id = fields.Many2one('res.users', string='Team')
    partner_id = fields.Many2one('res.partner', 'Client')
    establishment_id = fields.Many2one('res.partner', string='Establishment')
    plant_id = fields.Many2one('res.partner', string='Plant')
    lead_id = fields.Many2one('crm.lead', string='Lead')
    sale_id = fields.Many2one('sale.order', compute='_compute_sale_id')
    line_ids = fields.One2many('materials', 'wo_plant_id')
    pending_debts = fields.Boolean("Has pending debts", compute="_compute_pending_debts", store=False)

    worksheet_count = fields.Integer(compute='_compute_worksheet_count',
                                     string="Number of Worksheets")

    opened_worksheet_count = fields.Integer(compute='_compute_opened_worksheet_count',
                                            string="Number of Worksheets Opened")
    purchase_order_count = fields.Integer(compute='_compute_purchase_order_count', string="# Purchase Orders related")

    incident_count = fields.Integer(compute='_compute_incident_count',
                                    string="Number of Incidents")
    plant_picture = fields.Binary(related='plant_id.plant_picture')
    access_url = fields.Char(related="establishment_id.access_url")
    access_notifications = fields.Html(related="establishment_id.access_notifications")
    provisioned = fields.Boolean('Provisioned')
    access_done = fields.Boolean('Access done')

    certification_needed = fields.Boolean('Certification needed')
    checklist_fume_needed = fields.Boolean('Checklist fume needed')
    checklist_fire_needed = fields.Boolean('Checklist fire needed')

    employee_id = fields.Many2one('hr.employee', string='Employees')
    employee_ids = fields.Many2many('hr.employee', compute='_compute_employee_ids', string='Employees', store=False)
    allday = fields.Boolean("Apply all day long", default=True)
    worksheet_ids = fields.Many2many('worksheet.part')
    operators_notified = fields.Boolean('Operators Notified')
    plant_picture_1 = fields.Binary(string="Plant Picture 1", related='plant_id.plant_picture_1')
    plant_picture_2 = fields.Binary(string="Plant Picture 2", related='plant_id.plant_picture_2')
    plant_picture_3 = fields.Binary(string="Plant Picture 3", related='plant_id.plant_picture_3')
    plant_picture_4 = fields.Binary(string="Plant Picture 4", related='plant_id.plant_picture_4')

    list_id = fields.Many2one('material.list', compute='_compute_list_id')

    activity_ids = fields.One2many('mail.activity', 'res_id', string='Activities')

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
                if balance < 0:
                    rec.pending_debts = True

    def _compute_employee_ids(self):
        for rec in self:
            if rec.worksheet_ids:
                rec.employee_ids = rec.worksheet_ids.employee_id
            else:
                rec.employee_ids = False

    def _compute_list_id(self):
        for rec in self:
            rec.list_id = False
            if rec.lead_id:
                rec.list_id = self.env['material.list'].search([('lead_id', '=', rec.lead_id.id)])

    @api.onchange('lead_id')
    def _compute_sale_id(self):
        for rec in self:
            rec.sale_id = False
            if rec.lead_id:
                rec.sale_id = self.env['sale.order'].search(
                    [('opportunity_id', '=', rec.lead_id.id), ('state', '=', 'sale')], limit=1)

    @api.onchange('start_date', 'duration')
    def _compute_end_date(self):
        for rec in self:
            if rec.start_date and rec.duration:
                rec.end_date = rec.start_date + datetime.timedelta(hours=rec.duration)
            else:
                rec.end_date = False

    def _compute_purchase_order_count(self):
        for rec in self:
            rec.purchase_order_count = 0
            po = self.env['purchase.order'].search_count(
                [('opportunity_id', '=', rec.lead_id.id), ('po_selected', '=', True)])
            if po:
                rec.purchase_order_count = po

    def _compute_incident_count(self):
        for rec in self:
            rec.incident_count = 0
            incidents = self.env['incident'].search_count([('worksheet_id.id', 'in', self.worksheet_ids.ids)])
            if incidents:
                rec.incident_count = incidents

    def _compute_worksheet_count(self):
        for rec in self:
            rec.worksheet_count = 0
            worksheets = self.env['worksheet.part'].search_count([('workorder_plant_id', '=', rec.id)])

            if worksheets:
                rec.worksheet_count = worksheets

    def _compute_opened_worksheet_count(self):
        for rec in self:
            rec.opened_worksheet_count = self.env['work.order.plant'].search_count(
                [('state', '=', 'invoiced'), ('plant_id', '=', rec.plant_id.id)])

    def button_planned(self):
        for rec in self:
            if rec.state == 'to_plan':
                if rec.provisioned and rec.access_done:
                    rec.write({'state': 'to_hand'})
                else:
                    raise UserError(_('WO have to be provisioned and the access have to be done to handle.'))

    def button_handled(self):
        for rec in self:
            if rec.state == 'to_hand':
                rec.write({'state': 'in_process'})

    def button_finished(self):
        for rec in self:
            if rec.state == 'in_process':
                rec.write({'state': 'finished'})
                if rec.certification_needed:
                    rec.env['mail.activity'].create({
                        'display_name': _('Need Certification'),
                        'summary': _('You have to do the certification of ') + str(rec.name),
                        'date_deadline': datetime.datetime.now(),
                        'user_id': rec.user_id.id,
                        'res_id': rec.id,
                        'res_model_id': self.env['ir.model'].search([('model', '=', 'work.order.plant')], limit=1).id,
                        'activity_type_id': 4
                    })
                if rec.checklist_fume_needed:
                    self.env['checklist'].create({
                        'name': 'New',
                        'workorder_plant_id': rec.id,
                    })
                if rec.checklist_fire_needed:
                    self.env['checklist.fire'].create({
                        'name': 'New',
                        'workorder_plant_id': rec.id,
                    })

    def button_invoiced(self):
        for rec in self:
            if rec.state == 'finished':
                rec.write({'state': 'invoiced'})

    def button_reset(self):
        for rec in self:
            rec.write({'state': 'to_plan'})

    def button_notify_operators(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        for rec in self:
            if rec.operators_notified:
                raise UserError(_('Operators have been notified yet.'))
            template = self.env.ref('onmi_reliex_reports.onmi_mail_template_worksheet_clean_assign_work')
            for w in rec.worksheet_ids:
                template.send_mail(w.id, force_send=True)
            rec.operators_notified = True

    def action_worksheet_new(self):
        ctx = {
            'default_partner_id': self.partner_id.id,
            'default_establishment_id': self.establishment_id.id,
            'default_plant_id': self.plant_id.id,
            'default_workorder_plant_id': self.id,
            'default_part_type': 'plant',
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

    def action_create_invoice(self):
        for rec in self:
            for so in rec.lead_id.order_ids:
                invoice = so._create_invoices()
                sections = invoice.invoice_line_ids.filtered(lambda o: o.display_type == 'line_section')
                section_interesting = self.env['account.move.line']
                next_section = self.env['account.move.line']
                for s in sections:
                    if s.name == rec.plant_id.name:
                        section_interesting = s
                    elif section_interesting and s.sequence > section_interesting.sequence:
                        next_section = s
                        break
                if next_section:
                    lines_to_delete = invoice.invoice_line_ids.filtered(
                        lambda o: o.sequence > next_section.sequence or o.sequence < section_interesting.sequence)
                else:
                    lines_to_delete = invoice.invoice_line_ids.filtered(
                        lambda o: o.sequence < section_interesting.sequence)
                if lines_to_delete:
                    lines_to_delete.unlink()

    def action_without_function(self):
        return True

    def _get_employees(self):
        self.ensure_one()
        return ",".join([e for e in self.employee_ids.mapped("work_email") if e])

    def action_view_purchase_orders(self):
        action = self.env['ir.actions.actions']._for_xml_id("purchase.purchase_form_action")
        action['domain'] = [('opportunity_id.id', '=', self.lead_id.id), ('po_selected', '=', True)]
        return action

    def action_view_incident(self):
        action = self.env["ir.actions.actions"]._for_xml_id("onmi_reliex_operations.onmi_action_incident")
        action['domain'] = [('worksheet_id.id', 'in', self.worksheet_ids.ids)]
        return action

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val.get('name') == _('New') or val.get('name') == 'New':
                val['name'] = self.env['ir.sequence'].next_by_code('work.order.plant')
        return super().create(vals)
