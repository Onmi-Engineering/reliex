from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError

#defino clase que hereda de la original WorkOrderPlant
class MidWorkOrderPlant(models.Model):
    _inherit = 'work.order.plant'
    _description = 'Work order Plant Extension'

    is_new_created = fields.Boolean('Es creado nuevo?', default=False)

    worksheet_real_ids = fields.One2many('worksheet.part', inverse_name='workorder_plant_id')

    # Override _compute_end_date
    @api.onchange('start_date', 'duration')
    def _compute_end_date(self):
        super(MidWorkOrderPlant, self)._compute_end_date()
        if (self.is_new_created == False):
            self.is_new_created = True

    def action_create_invoice(self):
        # se debe poder facturar sin pasar por oportunidad, es decir, una OTI puede facturarse sin tener una oportunidad asociada
        # actualmente está iterando sobre rec.lead_id.order_ids, no debería tener en cuenta el "lead_id"
        for rec in self:
            if rec.lead_id.order_ids: #si posee lead, comportamiento normal
                super(MidWorkOrderPlant, self).action_create_invoice()
            else: #si no posee leads, crear factura independiente
                # Nueva lógica para facturar sin lead_id
                # Buscar todos los worksheets asociados a la Work Order
                worksheets = self.env['worksheet.part'].search([('workorder_plant_id', '=', rec.id)])
                # Si no hay worksheets, lanzar un error
                if not worksheets:
                    raise ValidationError(_('No hay partes de trabajo (worksheets) asociados a esta Orden de Trabajo.'))

                # Crear las líneas de factura a partir de las líneas de cada worksheet
                invoice_lines = []
                for worksheet in worksheets:
                    for line in worksheet.line_ids:
                        invoice_lines.append((0, 0, {
                            'name': line.product_id.name or f"Item de {worksheet.name}",
                            'quantity': line.qty_consumed or 1,
                            'price_unit': line.product_id.lst_price or 0.0,
                            'account_id': self.env['account.account'].search([], limit=1).id
                        }))

                # Si no hay líneas de factura generadas, lanzar un error
                if not invoice_lines:
                    raise ValidationError(
                        _('Los partes de trabajo (worksheets) no tienen líneas de materiales para facturar.'))

                # Crear la factura con las líneas generadas
                invoice_vals = {
                    'move_type': 'out_invoice',
                    'partner_id': rec.plant_id.id,  # Cliente de la Work Order
                    'invoice_origin': rec.name,  # Referencia de la Work Order
                    'invoice_date': date.today(),  # Fecha de factura = hoy
                    'invoice_line_ids': invoice_lines,  # Agregar las líneas de la factura
                }

                invoice = self.env['account.move'].create(invoice_vals)

                # Cambiar estado de la Work Order a "Invoiced"
                rec.write({'state': 'invoiced'})

                return {
                    'name': "Factura",
                    'view_mode': 'form',
                    'res_model': 'account.move',
                    'res_id': invoice.id,
                    'type': 'ir.actions.act_window',
                }
