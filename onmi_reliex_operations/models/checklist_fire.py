from odoo import fields, models, api, _


class ChecklistFire(models.Model):
    _name = 'checklist.fire'
    _description = 'Checklist fire of workorders plant'

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
    next_checking = fields.Char('Next checking', default=_('Anual'))
    checking_type = fields.Char('Checking type')

    # region SYSTEM CHECK
    charge_state = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')],
                                    'Checking the state of charge of the extinguishing agent in the extinguishing'
                                    ' container',
                                    required=True, default='ok')
    charge_state_comments = fields.Char('Comments')
    preassure_check = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')],
                                       'Checking the pressure of the extinguishing container', required=True,
                                       default='ok')
    preassure_check_comments = fields.Char('Comments')
    correct_opening = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')],
                                       'Verification of the correct opening of the ball valves of the main valve '
                                       'of the extinguishing container',
                                       required=True, default='ok')
    correct_opening_comments = fields.Char('Comments')
    correct_preassure = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')],
                                         'Checking the correct pressure of the detection line (end-of-line manometer)',
                                         required=True, default='ok')
    correct_preassure_comments = fields.Char('Comments')
    discharge_emitters = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')],
                                          'Verification that the discharge emitters '
                                          '(nozzles, sprinklers, diffusers, etc.) are in good condition and free '
                                          'of obstacles for their correct operation.',
                                          required=True,
                                          default='ok')
    discharge_emitters_comments = fields.Char('Comments')
    good_conditions = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')],
                                       'Verification of the good condition of the trip and alarm devices '
                                       '(if they exist)',
                                       required=True, default='ok')
    good_conditions_comments = fields.Char('Comments')
    signaling_circuits = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')], 'Checking the signaling circuits',
                                          required=True, default='ok')
    signaling_circuits_comments = fields.Char('Comments')
    check_components = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')],
                                        'Verification of the good state of the system components', required=True,
                                        default='ok')
    check_components_comments = fields.Char('Comments')
    general_cleaning = fields.Selection([('ok', 'O.K.'), ('comments', 'Comments')],
                                        'General cleaning of all components', required=True, default='ok')
    general_cleaning_comments = fields.Char('Comments')
    # endregion

    # region CORRECTIVE ACTIONS
    corrective_ids = fields.One2many('corrective.action', 'checklist_fire_id')
    # endregion
    normative = fields.Text('Normative', default=_('Normative:\n'
                                                   'Revisions carried out according to the maintenance program '
                                                   'specified in RD 513/2017,of May 22, which approves the Regulation'
                                                   ' of Fire Protection Installations.'))
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
