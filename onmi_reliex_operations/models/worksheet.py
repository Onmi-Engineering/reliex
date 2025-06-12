from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command


from datetime import timedelta
import pytz
import datetime


class Worksheet(models.Model):
    _name = 'worksheet.part'
    _description = 'Worksheets'
    _inherit = 'mail.thread'
    _rec_name = 'new_display_name'

    name = fields.Char(string='Worksheet Reference', default=lambda self: _('New'))
    new_display_name = fields.Char('New display Name', compute="_compute_new_display_name")
    comments = fields.Html("Comments")
    certified_comment = fields.Html("Observations")
    internal_comment = fields.Html("Internal comments")
    refuses_sign = fields.Boolean('Refuses to sign')

    part_type = fields.Selection([
        ('cleaning', 'Cleaning'),
        ('plant', 'Plant')
    ], string="Associated to")

    part_plant_type = fields.Selection([
        ('quotation', 'Quotation'),
        ('administration', 'Administration')
    ], string='Part Plant type')

    state = fields.Selection(string='Status', required=True, readonly=False, copy=False, tracking=True, selection=[
        ('to_do', 'To Do'),
        ('to_check', 'To Check'),
        ('done_and_check', 'Done & Checked')
    ], default='to_do',
                             help="The current state of your worksheet:\n"
                                  "\t- To Do: Init state \n"
                                      "\t- To Check: Worker fill all data and Worksheet is waiting for checking\n"
                                      "\t- Done & Checked: Filled and Checked.")

    line_ids = fields.One2many('materials', 'worksheet_id')
    # cleaning_line_ids = fields.Many2many('materials')
    cleaning_line_ids = fields.One2many('materials', 'worksheet_id')


    product_ref = fields.Many2one('product.template', "Product", required=True)

    workorder_id = fields.Many2one('work.order.clean', string='Cleanning Work Order')
    workorder_plant_id = fields.Many2one('work.order.plant', string='Plant Work Order')
    workorder_ids = fields.Many2many('work.order.plant', string='Plant Work Orders')
    partner_id = fields.Many2one('res.partner', string='Client')
    establishment_id = fields.Many2one('res.partner', string='Establishment')

    plant_id = fields.Many2one('res.partner', string='Plant')

    user_id = fields.Many2one('res.users', string='Boss Team')
    completion_date = fields.Datetime('Completion date')
    start_date = fields.Datetime(string='Start date')

    start_date_real = fields.Datetime('Start date', compute="_compute_start_date_real", store=True)
    # start_date_real = fields.Datetime(string='Start date')

    end_date = fields.Datetime(string='End date')
    duration = fields.Float(string='Duration')
    attachment_ids = fields.Many2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'worksheet')],
                                      string='Attachments')
    incident_ids = fields.One2many('incident', 'worksheet_id', string='Incidents')

    signature_client = fields.Binary(string='Signature Client')
    client_datas = fields.Char('Name, Surname & NIF')
    signature_commercial = fields.Binary(string='Signature Boss Team')
    commercial_datas = fields.Char('Name, Surname & NIF')

    allday = fields.Boolean("Apply all day long")
    employee_id = fields.Many2many('hr.employee', string='Employees')

    first_part = fields.Boolean(string='First Part')
    last_part = fields.Boolean(string='Last Part')

    handled = fields.Boolean('Handled', default=False)

    incident_count = fields.Integer(compute='_compute_incident_count',
                                    string="Number of Incidents")

    finished_plant_ids = fields.Many2many('res.partner')

    human_resources_ids = fields.Many2many('human.resources')
    operation_review = fields.Boolean('Checking of correct operation of kitchen equipment')
    action_protocol = fields.Text('Action protocol')

    alert_establishment_related = fields.Html(
        string='Alerta',
        related='establishment_id.alert_establishment',
        readonly=True
    )

    tec_vehicle = fields.Char(string="Vehículo")
    tec_oper1 = fields.Char(string="Nombre y Apellidos")
    tec_oper2 = fields.Char(string="Nombre y Apellidos")
    tec_date_init = fields.Datetime(string="Fecha y hora de inicio")
    tec_date_end = fields.Datetime(string="Fecha y hora de fin")
    tec_attachment = fields.Binary(string="Adjunto", required=True)

    def _compute_new_display_name(self):
        for rec in self:
            tz = self.env.user.tz
            rec.new_display_name = rec.name
            if rec.establishment_id:
                rec.new_display_name += " | " + rec.establishment_id.name
                if rec.plant_id and rec.plant_id.city:
                    rec.new_display_name += " - " + rec.plant_id.city
                if rec.establishment_id and rec.establishment_id.city and not rec.plant_id:
                    rec.new_display_name += " - " + rec.establishment_id.city
                if rec.end_date and rec.start_date:
                    hour_start = rec.start_date.astimezone(pytz.timezone(tz)).strftime('%H:%M')
                    hour_end = rec.end_date.astimezone(pytz.timezone(tz)).strftime('%H:%M')
                    rec.new_display_name += ' | ' + hour_start + ' - ' + hour_end
                if rec.user_id:
                    rec.new_display_name += ' | ' + rec.user_id.name
                if rec.employee_id:
                    rec.new_display_name += ' | '
                    for emp in rec.employee_id:
                        rec.new_display_name += emp.name + ', '
                    rec.new_display_name = rec.new_display_name[:-2]

    '''TO DO se comenta temporalmente esta funcion que calcula start_date_real para que si cae entre las 00 y 02 
    xlo lleve a las 03 sino no se muestra en calendario'''
    # @api.depends('start_date', 'workorder_id.start_date')
    # def _compute_start_date_real(self):
    #     for rec in self:
    #         tz = self.env.user.tz
    #         if rec.start_date:
    #             date_string = rec.start_date.astimezone(pytz.timezone(tz)).strftime('%Y-%m-%d %H:%M:%S')
    #             date_real = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    #             rec.write({
    #                 'start_date_real': date_real
    #             })
    #             # rec.start_date_real = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    #         else:
    #             rec.start_date_real = False

    @api.depends('start_date', 'workorder_id.start_date')
    def _compute_start_date_real(self):
        for rec in self:
            # Obtengo la zona horaria del usuario para convertir luego
            tz = self.env.user.tz
            if rec.start_date:
                # Convierto la fecha a la zona horaria del usuario
                local_start_date = rec.start_date.astimezone(pytz.timezone(tz))

                # Tomo la hora para comparar
                hour = local_start_date.hour

                # Si la hora está entre 22:00:00 y 23:59:59 le resto 2 horas
                if 22 <= hour < 24:
                    date_real = local_start_date - timedelta(hours=2)
                else:
                    # Sino mantengo la fecha original
                    date_real = local_start_date

                # Elimino la información de la zona horaria para cumplir con los requerimientos de Odoo
                naive_date_real = date_real.replace(tzinfo=None)

                rec.write({
                    'start_date_real': naive_date_real
                })
            else:
                rec.start_date_real = False

    def action_server_finish_workseet_cleaning(self):
        for rec in self:
            if rec.part_type != 'cleaning':
                raise UserError(_('This action only works on cleaning worksheets.'))
            rec.handled = True
            worksheet_related = self.env['worksheet.part'].search([('workorder_id', '=', rec.workorder_id.id)])
            not_finish_workorder = False
            for ws in worksheet_related:
                if ws.handled != True:
                    not_finish_workorder = True
                    break
            if not not_finish_workorder:
                rec.workorder_id.state = 'planned'

    def action_sign_info_act_window(self):
        if self.part_type != 'plant':
            action = self.env["ir.actions.actions"]._for_xml_id("onmi_reliex_operations.sign_info_act_window")
        else:
            action = self.env["ir.actions.actions"]._for_xml_id("onmi_reliex_operations.sign_info_act_window_plants")
        return action

    @api.depends('duration', 'start_date')
    def _compute_end_date(self):
        for rec in self:
            if rec.duration > 0.0 and rec.start_date:
                rec.end_date = rec.start_date + timedelta(hours=rec.duration)

    def _compute_incident_count(self):
        for rec in self:
            rec.incident_count = 0
            incidents = self.env['incident'].search_count([('worksheet_id', '=', rec.id)])
            if incidents:
                rec.incident_count = incidents

    def action_done(self):
        for rec in self:
            if rec.state == 'to_check':
                rec.write({'state': 'done_and_check'})
                # Revisión de si todos los partes de la OTL están finalizados, finalizar OTL asociada
                worksheets_otl = self.env['worksheet.part'].search([('workorder_id', '=', rec.workorder_id.id)])
                if rec.part_type == 'cleaning':
                    checked = True
                    for ws in worksheets_otl:
                        if ws.state != 'done_and_check':
                            checked = False
                            break
                    if checked and rec.workorder_id.state == 'to_finish':
                        rec.workorder_id.action_finished()
                        message = _(
                            "Se ha creado una nueva oportunidad por frecuencia")
                        return {
                            'type': 'ir.actions.client',
                            'tag': 'display_notification',
                            'params': {
                                'title': _('Oportunidad Creada'),
                                'message': message,
                                'sticky': True,
                                'type': 'success',
                                'next': {'type': 'ir.actions.act_window_close'},
                            }
                        }

    def action_checked(self):
        for rec in self:
            if rec.state == 'to_do' and rec.duration >= 0.5:
                # AGREGO ESTA CONDICION PORQUE SI NO DA ERROR
                if not rec.start_date:
                    raise UserError(_('Debe definir la fecha de inicio.'))
                rec.end_date = rec.start_date + timedelta(hours=rec.duration)
                rec.write({'state': 'to_check'})
                if rec.part_type == 'cleaning':
                    for line in rec.cleaning_line_ids:
                        workorder_line = rec.workorder_id.line_ids.filtered(
                            lambda l: l.product_id.id == line.product_id.id)
                        if workorder_line:
                            workorder_line[0].qty_on_parts += line.qty_consumed
                # Revisión de si todos los partes de la OTL están finalizados, finalizar OTL asociada
                worksheets_otl = self.env['worksheet.part'].search([('workorder_id', '=', rec.workorder_id.id)])
                if rec.part_type == 'cleaning':
                    done = True
                    for ws in worksheets_otl:
                        if ws.state not in ('to_check', 'done_and_check'):
                            done = False
                            break
                    if done and rec.workorder_id.state == 'handled':
                        rec.workorder_id.sudo().write({'state': 'to_finish'})
                else:
                    for line in rec.line_ids:
                        wo = rec.workorder_ids.filtered(lambda wo: wo.plant_id.id == line.plant_id.id)
                        line_wo = wo.line_ids.filtered(lambda wo_l: wo_l.product_id.id == line.product_id.id)
                        line_wo.qty_on_parts += line.qty_consumed
                    if rec.last_part:
                        wo_to_finish = rec.workorder_ids.filtered(
                            lambda wo: wo.plant_id.id in rec.finished_plant_ids.ids)
                        wo_to_finish.sudo().button_finished()
                rec.write({'state': 'to_check'})
                rec.write({'completion_date': fields.Datetime.now()})
            else:
                raise UserError(_('You have to fill duration on this worksheet.'))


    def action_reset(self):
        for rec in self:
            rec.write({'state': 'to_do'})
            if rec.part_type == 'cleaning':
                for line in rec.cleaning_line_ids:
                    workorder_line = rec.workorder_id.line_ids.filtered(
                        lambda l: l.product_id.id == line.product_id.id)
                    workorder_line.qty_on_parts -= line.qty_consumed

    def action_incident_new(self):
        ctx = {}
        if self.part_type == 'cleaning':
            ctx = {
                'default_partner_id': self.partner_id.id,
                'default_establishment_id': self.establishment_id.id,
                'default_plant_id': self.plant_id.id,
                'default_workorder_id': self.workorder_id.id,
                'default_worksheet_id': self.id,
            }
        if self.part_type == 'plant':
            ctx = {
                'default_partner_id': self.partner_id.id,
                'default_establishment_id': self.establishment_id.id,
                'default_plant_id': self.plant_id.id,
                'default_workorder_plant_id': self.workorder_plant_id.id,
                'default_worksheet_id': self.id,
            }
        return {
            'name': _('Create Incident'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'incident',
            'view_id': self.env.ref('onmi_reliex_operations.incident_form_view').id,
            'context': ctx,
        }

    def action_sign_worksheet(self):
        return True

    def action_view_incident(self):
        action = self.env["ir.actions.actions"]._for_xml_id("onmi_reliex_operations.onmi_action_incident")
        if self.part_type == 'cleaning':
            action['domain'] = [('worksheet_id.id', '=', self.id), ('plant_id', '=', self.plant_id.id)]
            action['context'] = {
                'default_worksheet_id': self.id,
                'default_plant_id': self.plant_id.id,
            }
        else:
            action['domain'] = [('worksheet_id.id', '=', self.id), ('establishment_id', '=', self.establishment_id.id)]
            action['context'] = {
                'default_worksheet_id': self.id,
                'default_establishment_id': self.establishment_id.id,
            }
        return action

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            # if val.get('name') == _('New') or val.get('name') == 'New':
            val['name'] = self.env['ir.sequence'].next_by_code('worksheet.part')
            val['duration'] = 8
        return super().create(vals)


    # Agregado para que cuando duplican copie las lineas, pedido por Ino en la tarea D22
    def copy_data(self, default=None):
        if default is None:
            default = {}
        if 'line_ids' not in default:
            default['line_ids'] = [
                Command.create(line.copy_data()[0])
                for line in self.line_ids
            ]
        return super().copy_data(default)

    # Agregado para que los usuarios que pertencen al grupo jefe de equipo no puedan modificar la instalacion
    @api.onchange('plant_id')
    def _onchange_plant_id(self):
        if self.env.user.has_group('onmi_reliex_operations.group_operation_boss_team_cleaning') and self._origin.plant_id:
            # Revertir al valor original si el usuario intenta cambiar el valor
            self.plant_id = self._origin.plant_id
            return {
                'warning': {
                    'title': 'Acceso restringido',
                    'message': 'Los jefes de equipo no tienen permisos para modificar este campo.'
                }
            }