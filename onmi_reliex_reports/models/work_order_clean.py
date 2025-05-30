from odoo import fields, models, api, _
import os, zipfile
import base64
from odoo.exceptions import ValidationError
import tempfile
from PIL import Image
from io import BytesIO
from odoo.exceptions import UserError


class WorkOrderClean(models.Model):
    _inherit = 'work.order.clean'

    def _get_attendee_emails_confirmed(self):
        """ Get comma-separated attendee email addresses from confirming WOC. """
        self.ensure_one()
        emails = ",".join([e for e in self.related_plant_ids.mapped("email") if e])
        if self.establishment_id.email:
            emails += ", " + self.establishment_id.email + ", "
        if self.establishment_id.parent_id.email:
            emails += ", " + self.establishment_id.parent_id.email
        return emails

    def _get_attendee_emails_reports(self):
        """ Get comma-separated attendee email addresses from sending reports WOC. """
        self.ensure_one()
        emails = ""
        if self.establishment_id.supervisor_email:
            emails += self.establishment_id.supervisor_email + ","
        if self.establishment_id.parent_id.email and self.establishment_id.parent_id.email not in emails:
            emails += self.establishment_id.parent_id.email + ","
        return emails

    def notify_operators(self):
        for rec in self:
            template = self.env.ref('onmi_reliex_reports.onmi_mail_template_worksheet_clean_assign_work')
            worksheets = self.env['worksheet.part'].search([('workorder_id.id', '=', self.id)])
            for w in worksheets:
                template.send_mail(w.id, force_send=True)

    def report_foto_zip(self):
        # Verifica que haya imágenes adjuntas
        if not self.env['worksheet.part'].search([('workorder_id.id', '=', self.id)]).attachment_ids:
            raise UserError("No hay imágenes adjuntas para generar el informe fotográfico.")

        # Crear un directorio temporal
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_filepath = os.path.join(temp_dir, "informe_fotográfico.zip")

            # Iterar sobre las imágenes adjuntas y guardarlas en el directorio temporal
            for part in self.env['worksheet.part'].search([('workorder_id.id', '=', self.id)]):
                for attachment in part.attachment_ids:
                    if attachment.mimetype   in 'png' or 'jpg' or 'jpeg':
                      if attachment.mimetype != 'application/pdf':  
                        print(attachment.mimetype)                       
                        image_data = base64.b64decode(attachment.datas)
                        image = Image.open(BytesIO(image_data))
                        # Guardar la imagen en el directorio temporal
                        image_filename = f"{attachment.name}"
                        image_filepath = os.path.join(temp_dir, image_filename)
                        if 'png' in attachment.mimetype.lower():
                            format = 'png'
                        if 'jpg' in attachment.mimetype.lower():
                            format = 'jpg'
                        if 'jpeg' in attachment.mimetype.lower():
                            format = 'jpeg'
                        if 'pdf' in attachment.mimetype.lower():
                            format = 'pdf'    
                        image.save(image_filepath, format=format)

            # Crear el archivo ZIP
            with zipfile.ZipFile(zip_filepath, 'w') as zipf:
                for part in self.env['worksheet.part'].search([('workorder_id.id', '=', self.id)]):
                    for attachment in part.attachment_ids:
                        if 'png' or 'jpg' or 'jpeg' in attachment.mimetype:
                          if attachment.mimetype != 'application/pdf':   
                            image_filename = f"{attachment.name}"
                            image_filepath = os.path.join(temp_dir, image_filename)
                            zipf.write(image_filepath, image_filename)

            # Leer el contenido del archivo ZIP
            with open(zip_filepath, 'rb') as zip_file:
                zip_content = zip_file.read()

            zip_filename = "informe_fotográfico.zip"

            # Crear el archivo adjunto en Odoo
            attachment = self.env['ir.attachment'].create({
                'name': zip_filename,
                'type': 'binary',
                'datas': base64.b64encode(zip_content).decode('utf-8'),
                'store_fname': zip_filename,
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'application/zip',
            })

            # Devolver la URL para descargar el archivo ZIP
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % (attachment.id),
                'target': 'self',
            }
