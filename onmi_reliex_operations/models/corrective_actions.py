from odoo import fields, models, api


class CorrectiveAction(models.Model):
    _name = 'corrective.action'
    _description = 'Corrective Actions'

    name = fields.Char('Number')

    corrective_action = fields.Char('Corrective  action')

    completion_date = fields.Date('Completion date')

    user_execute = fields.Char('User executes')

    checklist_id = fields.Many2one('checklist')
    checklist_fire_id = fields.Many2one('checklist.fire')
