from odoo import models, fields, _
from datetime import datetime, timedelta



class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    owner_type = fields.Selection([
        ("renting", "Renting"),
        ("own", "Propio")
    ], string="Contrato", default='own', tracking=True)
    itv_expiration = fields.Date(string="Vencimiento ITV", tracking=True)
    insurance_company = fields.Char(string="Compañia de seguro")
    insurance_expiration = fields.Date(string="Vencimiento del seguro", tracking=True)

    def _check_itv_expiration(self):
        today = fields.Date.today()
        expiration_date_30 = today + timedelta(days=30)

        # Buscar vehículos cuya ITV vence en 30 días
        vehicles = self.search([
            ('itv_expiration', '=', expiration_date_30),
            ('manager_id', '!=', False)
        ])

        # Plantilla de correo
        mail_template = self.env.ref('oeng_reliex_fleet.mail_template_itv_expiration_reminder')

        # Enviar correo a cada manager de los vehículos
        for vehicle in vehicles:
            mail_template.send_mail(vehicle.id, force_send=True)

        return True

    def _check_ins_expiration(self):
        today = fields.Date.today()
        expiration_date_30 = today + timedelta(days=30)

        # Buscar vehículos cuya ITV vence en 30 días
        vehicles = self.search([
            ('insurance_expiration', '=', expiration_date_30),
            ('manager_id', '!=', False)
        ])

        # Plantilla de correo
        mail_template = self.env.ref('oeng_reliex_fleet.mail_template_ins_expiration_reminder')

        # Enviar correo a cada manager de los vehículos
        for vehicle in vehicles:
            mail_template.send_mail(vehicle.id, force_send=True)

        return True