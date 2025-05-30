import datetime

from odoo import fields, models, api
import datetime


class WorksheetPart(models.Model):
    _inherit = 'worksheet.part'

    document_ids = fields.Many2many('documents.document',)
    folder_id = fields.Many2one('documents.folder', compute='_compute_folder_id', store=True)

    def _compute_folder_id(self):
        for rec in self:
            folder = self.env.ref('onmi_reliex_operations.documents_photo_report_folder')
            rec.folder_id = folder
