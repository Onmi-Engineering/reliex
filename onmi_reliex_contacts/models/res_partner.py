from odoo import fields, models, api, _

import datetime


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    # Diccionario de prefijos según el tipo
    TYPE_PREFIX_MAP = {
        'contact': 'Cli',
        'invoice': 'inv',
        'delivery': 'del',
        'followup': 'fol',
        'facturae_ac': 'fac',
        'other': 'oth',
        'establishment': 'Est',
        'plant': 'Ins'
    }

    partner_code = fields.Char(
        string='Código interno',
        compute='_compute_partner_code',
        store=True,
        readonly=True
    )

    new_display_name = fields.Char('New display Name', compute="_compute_new_display_name", store=False)
    type = fields.Selection(selection_add=[
        ('establishment', 'Establishment'),
        ('plant', 'Plant')
    ])

    contact_ids = fields.One2many('res.partner', 'parent_id', string='Contact',
                                  domain=[('active', '=', True), ('type', '=', 'contact'),
                                          ('company_type', '=', 'person')])
    policy_making_count = fields.Integer(compute='_compute_policy_making_count', string="Number of Policy-makings")
    incident_count = fields.Integer(compute='_compute_incident_count', string="Number of Incidents")
    plant_count = fields.Integer(compute='_compute_plant_count', string="Number of Plants")
    establishment_count = fields.Integer(string='# of Establishments', compute='_compute_establishment_count')
    list_material_count = fields.Integer(compute='_compute_list_material_count', string="Number of List Materials")

    plant_ids = fields.Many2many('res.partner', compute='_compute_plant_ids', string='Plants')
    plant_picture = fields.Binary(string="Plant Picture")
    plant_picture_1 = fields.Binary(string="Plant Picture 1")
    plant_picture_2 = fields.Binary(string="Plant Picture 2")
    plant_picture_3 = fields.Binary(string="Plant Picture 3")
    plant_picture_4 = fields.Binary(string="Plant Picture 4")

    frecuency_active = fields.Boolean(string='Quotations by frecuency active')
    delay = fields.Integer(string='Frecuency delay (days)', default=365)
    hour_open_establishment = fields.Float(string='Hora Apertura')
    hour_close_establishment = fields.Float(string='Hora Cierre')
    day_close = fields.Selection([
        ('lun', 'Lunes'),
        ('mar', 'Martes'),
        ('mie', 'Miércoles'),
        ('jue', 'Jueves'),
        ('vier', 'Viernes'),
        ('sab', 'Sábado'),
        ('dom', 'Domingo')
    ])

    # region DATOS TÉCNICOS

    extractor_ids = fields.One2many('extractor', 'plant_id', string="Extractors")
    duct_ids = fields.One2many('duct', 'plant_id', string="Ducts")
    cooker_hood_ids = fields.One2many('cooker.hood', 'plant_id', string="Cooker Hoods")

    access_url = fields.Char(string='Dealings')
    access_notifications = fields.Html('Notifications of access')
    # endregion
    # region más DATOS TÉCNICOS
    days_plant = fields.Integer(string='Days of Plant', default=0)

    days_clean = fields.Integer(string='Contracted days of Cleaning', default=0)

    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                     domain=[('res_model', '=', 'res.partner')],
                                     string='Attachments')

    technical_analysis = fields.Boolean('Technical analysis')
    noise_problems = fields.Boolean('Noise problems')
    price = fields.Float('Price')
    # endregion
    boss_name = fields.Char('Boss')
    supervisor_name = fields.Char('Supervisor')
    supervisor_email = fields.Char('Supervisor email')
    supervisor_phone = fields.Char('Supervisor phone')

    fictitious_customer = fields.Boolean('Fictitious customer')

    access_check = fields.Boolean(string='Saltar Acceso')

    # region PLANT DATA
    plant_type = fields.Selection([
        ('to_plant', 'To Plant'),
        ('to_clean', 'To clean')
    ], string='Plant type')

    access_vehicle = fields.Boolean(string='Acceso vehiculo', help="Autorización municipal para acceso vehículo")
    alert_establishment = fields.Html(string='Alerta establecimiento',
                                      help='Este alerta será visible solo si la Orden de trabajo esta en estado "Para planificar')
    # endregion

    # CORRECCION ERROR EN MAIN CON ESTA FUNCION
    # def _compute_new_display_name(self):
    #     for rec in self:
    #         rec.new_display_name = ''
    #         if rec.parent_id:
    #             rec.new_display_name += rec.parent_id.name + ' - ' + rec.name
    #         else:
    #             rec.new_display_name += rec.name

    def _compute_new_display_name(self):
        for rec in self:
            rec.new_display_name = ''
            parent_name = str(rec.parent_id.name) if rec.parent_id and rec.parent_id.name else ''
            name = str(rec.name) if rec.name else ''
            if parent_name:
                rec.new_display_name = parent_name + ' - ' + name
            else:
                rec.new_display_name = name

    # CORRECCION ERROR EN MAIN CON ESTA FUNCION

    def _compute_plant_count(self):
        for rec in self:
            if not rec.id:
                rec.plant_count = 0
                continue
            rec.plant_count = 0
            domain = [('parent_id.id', '=', self.id), ('type', '=', 'plant')]
            plants = self.env['res.partner'].search_count(domain)
            if plants:
                rec.plant_count = plants

    def _compute_establishment_count(self):
        for rec in self:
            if not rec.id:
                rec.establishment_count = 0
                continue
            rec.establishment_count = 0
            domain = [('parent_id.id', '=', self.id), ('type', '=', 'establishment')]
            establishments = self.env['res.partner'].search_count(domain)
            if establishments:
                rec.establishment_count = establishments

    def _compute_incident_count(self):
        for rec in self:
            if not rec.id:
                rec.incident_count = 0
                continue
            rec.incident_count = 0
            domain = ['|', '|', ('partner_id.id', '=', self.id), ('establishment_id', '=', self.id),
                      ('plant_id', '=', self.id)]
            incidents = self.env['incident'].search_count(domain)
            if incidents:
                rec.incident_count = incidents

    def _compute_list_material_count(self):
        for rec in self:
            rec.list_material_count = 0
            domain = [('plant_id.id', '=', self.id)]
            list_materials = self.env['material.list'].search_count(domain)
            if list_materials:
                rec.list_material_count = list_materials

    def _compute_plant_ids(self):
        for rec in self:
            rec.plant_ids = False
            if rec.child_ids:
                for child in rec.child_ids:
                    if child.child_ids:
                        for ch in child.child_ids:
                            if ch.type == 'plant':
                                rec.plant_ids = [(4, ch.id)]

    def action_view_incidents(self):
        action = self.env["ir.actions.actions"]._for_xml_id("onmi_reliex_operations.onmi_action_incident")
        action['domain'] = ['|', '|', ('partner_id.id', '=', self.id), ('establishment_id', '=', self.id),
                            ('plant_id', '=', self.id)]
        return action

    def action_view_plants(self):
        action = self.env["ir.actions.actions"]._for_xml_id("onmi_reliex_contacts.action_plants")
        action['context'] = {
            'default_parent_id': self.id,
            'default_type': 'plant'
        }
        return action

    def action_view_establishment(self):
        action = self.env["ir.actions.actions"]._for_xml_id("onmi_reliex_contacts.action_establishment")
        action['context'] = {
            'default_parent_id': self.id,
            'default_type': 'establishment',
        }
        return action

    def action_view_list_materials(self):
        action = self.env["ir.actions.actions"]._for_xml_id("onmi_reliex_operations.material_list_act_window")
        action['domain'] = [('plant_id', '=', self.id)]
        action['context'] = {
            'default_plant_id': self.id,
        }
        return action

    def cron_create_leads_frecuency(self):
        establishments_frecuency = self.env['res.partner'].search(
            [('active', '=', True), ('type', '=', 'establishment'), ('frecuency_active', '=', True)])
        stage_frecuency = self.env['crm.stage'].search([('frecuency', '=', True)])
        for rec in establishments_frecuency:
            last_workorder = self.env['work.order.clean'].search(
                [('establishment_id', '=', rec.id)], order='end_date')
            lead_frecuency = self.env['crm.lead'].search(
                [('partner_id', '=', rec.id), ('stage_id.is_won', '=', False), ('created_by_frecuency', '=', True)])
            if last_workorder and not lead_frecuency and last_workorder[-1].end_date:
                last_workorder = last_workorder[-1]
                days_diff = datetime.datetime.now() - last_workorder.end_date
                days_diff = days_diff.total_seconds() / (24 * 60 * 60)
                if rec.delay <= days_diff:
                    info = _('Last Workorder: ') + last_workorder.name + _('\nPlants that had been cleaned:\n')
                    info_plants = ''
                    for p in last_workorder.related_plant_ids:
                        info_plants += '    - ' + p.name + '\n'
                    info += info_plants
                    lead_data = {
                        'name': _('Lead created by Frecuency'),
                        'partner_id': rec.id,
                        'plant_ids': last_workorder.related_plant_ids.ids,
                        'type': 'opportunity',
                        'stage_id': stage_frecuency.id,
                        'wo_type': 'cleaning',
                        'description': info,
                        'created_by_frecuency': True,
                    }
                    self.env['crm.lead'].create(lead_data)

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if 'type' in val:
                if val['type'] == 'establishment':
                    val['access_notifications'] = _("<p>" \
                                                    "<strong>User:</strong><br/>" \
                                                    "<strong>Password:</strong><br/>" \
                                                    "<strong>Tfno:</strong><br/>" \
                                                    "<strong>Contact:</strong><br/>" \
                                                    "<strong>Mail:</strong><br/></p>")
        return super().create(vals)


    @api.model
    def _get_sequence_prefix(self, partner_type):
        # Obtengo el siguiente número de secuencia para un tipo específico
        if not partner_type:
            return False

        prefix = self.TYPE_PREFIX_MAP.get(partner_type, 'oth')
        sequence = self.env['ir.sequence'].search([
            ('code', '=', f'res.partner.{partner_type}'),
            ('prefix', '=', prefix)
        ], limit=1)

        if not sequence:
            sequence = self.env['ir.sequence'].create({
                'name': f'Secuencia Partner {partner_type}',
                'code': f'res.partner.{partner_type}',
                'prefix': prefix,
                'padding': 4
            })

        return sequence.next_by_id()


    @api.depends('type')
    def _compute_partner_code(self):
        """Calcula el código del partner basado en su tipo"""
        for partner in self:
            if not partner.partner_code:  # Solo calcula si no tiene código
                if partner.type:
                    partner.partner_code = self._get_sequence_prefix(partner.type)
                else:
                    partner.partner_code = self._get_sequence_prefix('other')