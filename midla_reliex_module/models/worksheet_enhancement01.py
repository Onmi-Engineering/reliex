from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Worksheet(models.Model):
    _inherit = 'worksheet.part'

    worksheet_message_ids = fields.One2many('worksheet.message', 'worksheet_id', string='Messages')
    plant_comment = fields.Html(related='plant_id.comment', string="Plant comment", store=True)

    def _check_attachment(self):
        pass

    @api.model
    def create(self, vals):
        # Call the attachment check before creating the record
        record = super(Worksheet, self).create(vals)
        record._check_attachment()
        return record

    def write(self, vals):
        # Call the attachment check before updating the record
        res = super(Worksheet, self).write(vals)
        self._check_attachment()
        return res

class WorksheetMessage(models.Model):
    _name = 'worksheet.message'
    _description = 'Worksheet Message'

    worksheet_id = fields.Many2one('worksheet.part', string='Worksheet', required=True,
                                   ondelete='cascade')
    message_text = fields.Text(string='Message', required=True)
    message_date = fields.Datetime(string='Date', default=fields.Datetime.now)
    author_id = fields.Many2one('res.users', string='Author', default=lambda self: self.env.user)
