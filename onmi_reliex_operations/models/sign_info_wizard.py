from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SignInfoWizard(models.TransientModel):
    _name = 'sign.info.wizard'
    _description = 'Sign Wizard'

    start_date = fields.Datetime(string='Start date', related='worksheet_id.start_date')
    end_date = fields.Datetime(string='End date', related='worksheet_id.end_date')
    duration = fields.Float(string='Duration', related='worksheet_id.duration')
    worksheet_id = fields.Many2one('worksheet.part')
    establishment_id = fields.Many2one(related='worksheet_id.establishment_id')
    plant_id = fields.Many2one('res.partner', string='Plant', related='worksheet_id.plant_id')
    user_id = fields.Many2one('res.users', string='Boss Team', related='worksheet_id.user_id')
    certified_comment = fields.Html('Certified comments', related='worksheet_id.certified_comment')
    comments = fields.Html('Comments', related='worksheet_id.comments')
    part_type = fields.Selection(related='worksheet_id.part_type')
    incident_ids = fields.Many2many('incident', string='Incidents', compute='_compute_incident_ids',
                                    store=True)
    # resource_ids = fields.Many2many('materials', related='worksheet_id.cleaning_line_ids')
    resource_ids = fields.One2many('materials', related='worksheet_id.cleaning_line_ids')
    line_ids = fields.One2many(related='worksheet_id.line_ids')
    operation_review = fields.Boolean('Checking of correct operation of kitchen equipment')

    signature_client = fields.Binary(string='Signature Client')
    signature_commercial = fields.Binary(string='Signature Boss Team')
    refuses_sign = fields.Boolean('Refuses to sign')
    client_datas = fields.Char('Name, Surname & NIF')
    commercial_datas = fields.Char('Name, Surname & NIF', compute="_compute_commercial_datas", store=True)

    worksheet_name = fields.Char('Worksheet Name', related='worksheet_id.name')

    filters_with_photo = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ('not_applicable', 'Not applicable'),
    ], string="Filters placed with photo", required=True)

    registers_closed = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ('not_applicable', 'Not applicable'),
    ], string="Registers closed and checked", required=True)

    gas_hose_checked = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ('not_applicable', 'Not applicable'),
    ], string="Gas hose checked", required=True)

    gas_depressor_checked = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ('not_applicable', 'Not applicable'),
    ], string="Gas depressor checked", required=True)

    devices_checked = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ('not_applicable', 'Not applicable'),
    ], string="Devices checked (Fryer, plates, Broiler, Extractor, etc.)", required=True)

    @api.depends('worksheet_id')
    def _compute_commercial_datas(self):
        for rec in self:
            rec.commercial_datas = ''
            if rec.worksheet_id:
                if rec.worksheet_id.user_id:
                    rec.commercial_datas += rec.worksheet_id.user_id.name
                    if rec.worksheet_id.user_id.employee_id.identification_id:
                        rec.commercial_datas += ", " + rec.worksheet_id.user_id.employee_id.identification_id

    @api.depends('worksheet_id')
    def _compute_incident_ids(self):
        for rec in self:
            if rec.worksheet_id:
                incidents = rec.worksheet_id.incident_ids.filtered(
                    lambda i: i.incident_type != 'reliex_info' and i.state != 'not_handling')
                rec.incident_ids = incidents

    def confirm_sign_and_send(self):
        self.ensure_one()
        if not self.operation_review:
            raise UserError(_('You have to check kitchen operations before done the sign.'))
        if not self.refuses_sign and not self.signature_client:
            raise UserError(_('You have to fill the signature client if not refuses to sign.'))
        if not self.refuses_sign and not self.client_datas:
            raise UserError(_('You have to fill name of client if not refuses to sign.'))

        self.worksheet_id.write({
            'signature_client': self.signature_client,
            'client_datas': self.client_datas,
            'refuses_sign': self.refuses_sign,
            'signature_commercial': self.signature_commercial,
            'commercial_datas': self.commercial_datas,
            'operation_review': self.operation_review,
        })
