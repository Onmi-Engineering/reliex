from odoo import fields, models, api, _

import base64


class WorkOrderClean(models.Model):
    _inherit = 'work.order.clean'

    def action_generate_attachment(self):
        super(WorkOrderClean, self).action_generate_attachment()

        REPORT_ID = 'onmi_reliex_photo_report.action_report_photographical'
        pdf = self.env['ir.actions.report']._render_qweb_pdf(REPORT_ID, self.ids)[0]
        b64_pdf = base64.b64encode(pdf)
        ATTACHMENT_NAME = _('Photographical Report' + '/' + self.name[0] + '.pdf')
        self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'store_fname': ATTACHMENT_NAME,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })


