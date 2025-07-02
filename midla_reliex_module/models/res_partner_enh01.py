from odoo import models, fields, api, _

class RespartnerEnhancement(models.Model):
    _inherit = 'res.partner'

    invoice_email = fields.Char(string="Email Factura",
                                help="Este correo se utiliza para enviar la facturación al cliente.")
    certif_email = fields.Char(string="Email Certificado",
                               help="Este correo se utiliza para enviar certificados.")
    stablish_email = fields.Char(string="Email Establecimiento",
                                 help="Este correo se utiliza para enviar notificaciones de las OT a los establecimientos.")
