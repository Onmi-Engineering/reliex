from odoo import models, fields, api, _
from odoo.exceptions import UserError


class QuotationSelectionWizard(models.TransientModel):
    _name = 'quotation.selection.wizard'
    _description = 'Wizard para seleccionar presupuesto a confirmar'

    lead_id = fields.Many2one('crm.lead', string='Oportunidad', required=True)
    quotation_ids = fields.Many2many('sale.order', string='Presupuestos Disponibles')
    selected_quotation_id = fields.Many2one(
        'sale.order',
        string='Presupuesto a Confirmar',
        required=True,
        domain="[('id', 'in', quotation_ids)]"
    )

    def action_confirm_selected_quotation(self):
        """Confirmar el presupuesto seleccionado"""
        self.ensure_one()

        if not self.selected_quotation_id:
            raise UserError(_('Debe seleccionar un presupuesto para confirmar.'))

        # Confirmar el presupuesto seleccionado
        self.selected_quotation_id.action_confirm()

        # Retornar mensaje de confirmación
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Presupuesto Confirmado'),
                'message': _('El presupuesto %s ha sido confirmado correctamente.') % self.selected_quotation_id.name,
                'type': 'success',
                'sticky': True,
            }
        }

    def action_close_wizard(self):
        """Cerrar el wizard"""
        return {'type': 'ir.actions.act_window_close'}