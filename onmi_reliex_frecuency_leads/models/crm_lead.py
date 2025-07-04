from odoo import fields, models, api, _
from odoo.exceptions import UserError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    has_quotation_incidents = fields.Boolean('Has quotation incidents', compute='_compute_has_quotation_incidents')
    client_id = fields.Many2one('res.partner')
    parent_partner_id = fields.Many2one('res.partner', compute='_compute_parent_partner_id', store=True)
    created_by_incident = fields.Boolean('Created by incident', store=True)

    related_invoice_ids = fields.Many2many(
        'account.move',
        string='Facturas relacionadas',
        related='order_ids.invoice_ids',
        readonly=True,
    )

    # Campo booleano para indicar si tiene facturas
    has_invoice = fields.Boolean(
        string='Tiene facturas',
        compute='_compute_has_invoice',
        store=True,
    )

    ##########D36
    # Campo computado para contar presupuestos
    quotation_count = fields.Integer(
        string='Número de Presupuestos',
        compute='_compute_quotation_count'
    )

    ##########D36

    # Función para calcular si tiene facturas
    @api.depends('related_invoice_ids')
    def _compute_has_invoice(self):
        for lead in self:
            lead.has_invoice = len(lead.related_invoice_ids) > 0

    @api.depends('partner_id')
    def _compute_parent_partner_id(self):
        for rec in self:
            if rec.partner_id:
                rec.parent_partner_id = rec.partner_id.parent_id
                rec.client_id = rec.partner_id.parent_id
            else:
                rec.parent_partner_id = False

    def _compute_has_quotation_incidents(self):
        for rec in self:
            quotation_incidents = self.env['incident'].search(
                [('establishment_id', '=', rec.partner_id.id), ('incident_type2', '=', 'quotation'), ('state', '!=', 'finished')])
            rec.has_quotation_incidents = True if quotation_incidents else False

    def button_generate_partner(self):
        if not self.partner_id:
            raise UserError(_('You cant generate client if you dont define establishment.'))
        self.client_id = self.env['res.partner'].create({
            'name': _('VAT of ') + self.partner_id.name,
            'is_company': True,
        })
        self.partner_id.write({
            'is_company': True,
        })
        self.partner_id.parent_id = self.client_id

    def action_show_incident_related(self):
        action = super(CrmLead, self).action_show_incident_related()
        action['context'] = {
            'create': 0,
            'search_default_not_handling_quot_incidents': 1,
        }
        return action

    # def action_set_won_rainbowman(self):
    #     res = super(CrmLead, self).action_set_won_rainbowman()
    #     frecuency_lead = self.env['frecuency.lead'].search([('lead_id', '=', self.id)])
    #     if frecuency_lead:
    #         woc_lead = self.env['work.order.clean'].search([('lead_id', '=', self.id)])
    #         frecuency_lead.write({
    #             'workorder_id': woc_lead.id,
    #         })
    #     return res

    _skip_won_stage_validation = False

    # El metodo onchange para la interfaz de formulario
    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        """
        Evita que se cambie una oportunidad a una etapa con is_won = True
        desde el formulario y muestra un mensaje de error personalizado.
        """
        # Si el cambio viene de action_set_won_rainbowman, permitir el cambio
        if self.env.context.get('skip_won_stage_validation', False):
            return

        if self.stage_id and self.stage_id.is_won:
            # Revertir al stage_id anterior
            if self._origin.stage_id:
                self.stage_id = self._origin.stage_id

            # Lanzar mensaje de error
            raise UserError(_("No se puede mover una oportunidad a la etapa GANADO, siga el flujo establecido."))

    # Sobrescribir el metodo write para interceptar cambios desde la vista kanban
    def write(self, vals):
        """
        Sobrescribe el metodo write para evitar que se arrastre una oportunidad
        a una etapa con is_won = True desde la vista kanban.
        """
        # Si el cambio viene de action_set_won_rainbowman, permitir el cambio
        if self.env.context.get('skip_won_stage_validation', False):
            return super(CrmLead, self).write(vals)

        if 'stage_id' in vals:
            new_stage = self.env['crm.stage'].browse(vals['stage_id'])
            if new_stage.is_won:
                raise UserError(_("No se puede mover una oportunidad a la etapa GANADO, siga el flujo establecido."))

        return super(CrmLead, self).write(vals)

    def action_set_won_rainbowman(self):
        """
        Sobrescribe el metodo action_set_won_rainbowman para permitir
        el cambio a etapa ganada cuando se ejecuta esta acción específica.
        """
        # Añadir contexto para saltarse la validación desde el boton GANADO
        self = self.with_context(skip_won_stage_validation=True)

        # Ejecutar la funcien original
        res = super(CrmLead, self).action_set_won_rainbowman()

        # Genera OTL en work.order.clean
        frecuency_lead = self.env['frecuency.lead'].search([('lead_id', '=', self.id)])
        if frecuency_lead:
            woc_lead = self.env['work.order.clean'].search([('lead_id', '=', self.id)])
            if woc_lead:
                frecuency_lead.write({
                    'workorder_id': woc_lead.id,
                })

    ##########D36
    @api.depends('order_ids')
    def _compute_quotation_count(self):
        for lead in self:
            lead.quotation_count = len(lead.order_ids.filtered(lambda o: o.state in ['draft', 'sent']))

    def action_confirm_quotations(self):
        """Acción para confirmar presupuestos asociados a la oportunidad"""
        self.ensure_one()

        # Obtener presupuestos en estado borrador o enviado
        quotations = self.order_ids.filtered(lambda o: o.state in ['draft', 'sent'])

        if not quotations:
            raise UserError(_('No hay presupuestos pendientes de confirmación para esta oportunidad.'))

        if len(quotations) == 1:
            # Si hay solo un presupuesto, confirmarlo directamente
            quotation = quotations[0]
            quotation.action_confirm()

            # Mostrar mensaje sticky
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Presupuesto Confirmado'),
                    'message': _('El presupuesto %s ha sido confirmado correctamente.') % quotation.name,
                    'type': 'success',
                    'sticky': True,
                }
            }
        else:
            # Si hay múltiples presupuestos, abrir wizard de selección
            return {
                'type': 'ir.actions.act_window',
                'name': _('Seleccionar Presupuesto a Confirmar'),
                'res_model': 'quotation.selection.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_lead_id': self.id,
                    'default_quotation_ids': [(6, 0, quotations.ids)]
                }
            }
    ##########D36