from odoo import models, fields, api, _

class RespartnerEnhancement(models.Model):
    _inherit = 'res.partner'

    invoice_email = fields.Char(string="Email Factura")
    certif_email = fields.Char(string="Email Certificado")
    stablish_email = fields.Char(string="Email Establecimiento")

