from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    liters = fields.Integer(string="Litros repostados")
    ticket = fields.Binary(string="Ticket")

    @api.constrains('service_type_id', 'liters', 'amount')
    def _check_required_fields_for_repostaje(self):
        for record in self:
            if record.service_type_id and record.service_type_id.name == 'Repostaje':
                if not record.liters:
                    raise ValidationError(
                        _("El campo 'Litros repostados' es obligatorio para el tipo de servicio 'Repostaje'."))
                if not record.amount:
                    raise ValidationError(_("El campo 'Importe' es obligatorio para el tipo de servicio 'Repostaje'."))

    @api.onchange('odometer')
    def _check_odometer_difference(self):
        for record in self:
            if record.vehicle_id and record.odometer:
                vehicle_odometer = record.vehicle_id.odometer
                difference = record.odometer - vehicle_odometer

                if difference > 2000:
                    return {
                        'warning': {
                            'title': 'Diferencia de odómetro significativa',
                            'message': 'La diferencia entre el odómetro ingresado ({:.2f}) y el odómetro del vehículo ({:.2f}) es superior a 2000.00 km ({:.2f}).'.format(
                                record.odometer, vehicle_odometer, difference)
                        }
                    }

    @api.onchange('service_type_id')
    def _onchange_service_type_id(self):
        if self.service_type_id:
            self.description = self.service_type_id.name
            # Limpia el campo liters si no es un repostaje
            if self.service_type_id.name != 'Repostaje':
                self.liters = False

    @api.model
    def create(self, vals):
        service_type = self.env['fleet.service.type'].browse(vals.get('service_type_id'))
        if service_type and not vals.get('description'):
            vals['description'] = service_type.name
        if service_type and service_type.name != 'Repostaje':
            vals['liters'] = False
        return super().create(vals)

    def write(self, vals):
        for record in self:
            if 'service_type_id' in vals:
                service_type = self.env['fleet.service.type'].browse(vals['service_type_id'])
                if service_type:
                    if 'description' not in vals:
                        vals['description'] = service_type.name
                    if service_type.name != 'Repostaje':
                        vals['liters'] = False
        return super().write(vals)

    @api.onchange('vehicle_id')
    def _check_vehicle_itv_expiration(self):
        for record in self:
            if record.vehicle_id and record.vehicle_id.itv_expiration:
                today = fields.Date.today()
                days_difference = (record.vehicle_id.itv_expiration - today).days

                # Si la fecha de ITV es igual o menor a 30 días respecto a la fecha actual
                if 0 <= days_difference <= 30:
                    # Crear mensaje de advertencia
                    expiration_date = record.vehicle_id.itv_expiration.strftime('%d/%m/%Y')
                    message = f"ATENCIÓN: La ITV del vehículo {record.vehicle_id.name} está próxima a vencer. "
                    message += f"Fecha de vencimiento: {expiration_date} (en {days_difference} días)."

                    return {
                        'warning': {
                            'title': 'ITV próxima a vencer',
                            'message': message
                        }
                    }
                # Si la ITV ya está vencida
                elif days_difference < 0:
                    expiration_date = record.vehicle_id.itv_expiration.strftime('%d/%m/%Y')
                    message = f"ADVERTENCIA: La ITV del vehículo {record.vehicle_id.name} está VENCIDA. "
                    message += f"Fecha de vencimiento: {expiration_date} (hace {abs(days_difference)} días)."

                    return {
                        'warning': {
                            'title': 'ITV VENCIDA',
                            'message': message
                        }
                    }