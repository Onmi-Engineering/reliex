from odoo import models, api, _, http
from markupsafe import escape
from lxml import etree
from odoo.http import request


class Invite(models.TransientModel):
    _inherit = 'mail.wizard.invite'


    # Heredo la funcion original y la reemplazo por esta.
    @api.model
    def default_get(self, fields):
        result = super(Invite, self).default_get(fields)
        if 'message' not in fields:
            return result

        user_name = self.env.user.display_name
        model = result.get('res_model')
        res_id = result.get('res_id')

        # Capturo la URL base del actual registro
        current_url = request.httprequest.url_root.rstrip('/')

        if model and res_id:
            document = self.env['ir.model']._get(model).display_name
            title = self.env[model].browse(res_id).display_name

            # Creo la URL al registro específico basado en la URL actual
            record_url = f"{current_url}/web#id={res_id}&model={model}&view_type=form"

            # Construye el mensaje con el enlace
            msg_text = _('%(user_name)s le invitó a seguir %(document)s el documento: ') % {
                'user_name': user_name,
                'document': document
            }

            # Creo el mensaje HTML de forma controlada
            message = etree.Element("div")
            p1 = etree.SubElement(message, "p")
            p1.text = _("Hola,")

            p2 = etree.SubElement(message, "p")
            p2.text = msg_text

            # Creo la etiqueta <a> manualmente dentro del parrafo
            link = etree.SubElement(p2, "a", href=record_url)
            link.text = title

        else:
            # Caso generico cuando no hay modelo o res_id
            message = etree.Element("div")
            p1 = etree.SubElement(message, "p")
            p1.text = _("Hello,")

            p2 = etree.SubElement(message, "p")
            p2.text = _('%(user_name)s le invitó a seguir un nuevo documento.') % {
                'user_name': user_name
            }

        # Lo converierto a cadena HTML
        result['message'] = etree.tostring(message, encoding='unicode', method='html')

        return result
