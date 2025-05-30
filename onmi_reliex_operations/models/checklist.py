from odoo import fields, models, api, _


class Checklist(models.Model):
    _name = 'checklist'
    _description = 'Checklist of workorders plant'

    name = fields.Char('Name', default=lambda self: _('New'))

    state = fields.Selection([
        ('new', 'New'),
        ('finished', 'Finished')
    ], default="new", string="State")

    workorder_plant_id = fields.Many2one('work.order.plant')
    partner_id = fields.Many2one('res.partner', 'Client', related='workorder_plant_id.partner_id')
    plant_id = fields.Many2one('res.partner', related='workorder_plant_id.plant_id')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    inspection_date = fields.Date('Inspection date')
    details = fields.Char('Details of works to do')

    # region DUCTS
    hung_distance = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Hung distance', required=True,
                                     default='ok')
    holder = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Holders', required=True, default='ok')
    joints = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'joints', required=True, default='ok')
    cracks = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Cracks, oxide, general state', required=True,
                              default='ok')
    staples = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Staples', required=True, default='ok')
    others = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Others (specify)', required=True,
                              default='ok')
    hung_distance_comments = fields.Char('Hung distance comments')
    holder_comments = fields.Char('Comments')
    joints_comments = fields.Char('Comments')
    staples_comments = fields.Char('Comments')
    cracks_comments = fields.Char('Comments')
    others_comments = fields.Char('Comments')
    # endregion

    # region EXIT DUCTS
    cracks_ducts = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Cracks, oxide, general state',
                                    required=True, default='ok')

    others_1 = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Others (specify)', required=True,
                                default='ok')
    others_2 = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Others (specify)', required=True,
                                default='ok')
    cracks_ducts_comments = fields.Char('Comments')
    others_1_comments = fields.Char('Comments')
    others_2_comments = fields.Char('Comments')
    # endregion

    # region MACHINE
    holder_machine = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Holders', required=True, default='ok')
    joints_machine = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'joints', required=True, default='ok')
    cracks_machine = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Cracks, oxide, general state',
                                      required=True, default='ok')
    others_machine = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Others (specify)', required=True,
                                      default='ok')
    holder_machine_comments = fields.Char('Comments')
    joints_machine_comments = fields.Char('Comments')
    cracks_machine_comments = fields.Char('Comments')
    others_machine_comments = fields.Char('Comments')
    # endregion

    # region WORKING
    seal_ducts = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Seal ducts', required=True, default='ok')
    seal_machine = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Seal machine & joints', required=True,
                                    default='ok')
    exit_duct = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Exit ducts & cap nuts', required=True,
                                 default='ok')
    seal_ducts = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Seal ducts', required=True, default='ok')
    seal_machine = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Seal machine & joints', required=True,
                                    default='ok')
    exit_duct = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Exit ducts & cap nuts', required=True,
                                 default='ok')
    seal_ducts_comments = fields.Char('Comments')
    seal_machine_comments = fields.Char('Comments')
    exit_duct_comments = fields.Char('Comments')
    seal_ducts_comments = fields.Char('Comments')
    seal_machine_comments = fields.Char('Comments')
    exit_duct_comments = fields.Char('Comments')
    # endregion
    general_others_1 = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Others (specify)', required=True,
                                      default='ok')
    general_others_2 = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Others (specify)', required=True,
                                      default='ok')
    general_others_1_comments = fields.Char('Comments')
    general_others_2_comments = fields.Char('Comments')

    # region CORRECTIVE ACTIONS
    corrective_ids = fields.One2many('corrective.action', 'checklist_id')
    # endregion
    # region RESOLUTION
    accepted = fields.Boolean('Accepted')
    refused = fields.Boolean('Refused')
    # endregion
    # region SIGNATURES
    checked_by = fields.Char('Checked by')
    endorsed_by = fields.Char('Endorsed by')
    signature_checked = fields.Binary(string='Signature checked')
    signature_endorsed = fields.Binary(string='Signature endorsed')
    checked_date = fields.Date('Checked date')
    endorsed_date = fields.Date('Endorsed date')

    # endregion

    def button_finish(self):
        for rec in self:
            if rec.state == 'new':
                rec.write({'state': 'finished'})

    def button_reset(self):
        for rec in self:
            rec.write({'state': 'new'})

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val.get('name') == _('New') or val.get('name') == 'New':
                val['name'] = self.env['ir.sequence'].next_by_code('checklist')
        return super().create(vals)
