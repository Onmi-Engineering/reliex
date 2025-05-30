from odoo import fields, models, api, _
from datetime import datetime, timedelta


class FrecuencyLead(models.Model):
    _name = 'frecuency.lead'
    _description = 'Leads of frecuency'
    _order = 'status, calculated_date'

    name = fields.Char('Name', required=1)
    establishment_id = fields.Many2one('res.partner', domain=[('type', '=', 'establishment')], required=1)
    establishment = fields.Char(related='establishment_id.name', string="Establishment", store=True)
    state_id = fields.Many2one(related='establishment_id.state_id', store=True)
    city = fields.Char(related='establishment_id.city', store=True)
    # calculated_date = fields.Date('Next cleanning date')
    calculated_date = fields.Date(string='Fecha calculada', compute='recalculate_dates', store=True)
    last_workorder_date = fields.Date('Last workorder date', help="Start date of last workorder of this establishment.")
    delay = fields.Integer(related='establishment_id.delay', store=True)
    full_cleanning_days = fields.Integer('Days of full cleaning', compute='_compute_full_cleanning_days')
    status = fields.Selection([
        ("current", "Current"),
        ("expired", "Expired"),
        ("created", "Generada"),
    ], default='current')
    previous_workorder_id = fields.Many2one('work.order.clean', string='Previous WOC', required=1)
    workorder_id = fields.Many2one('work.order.clean', string='WOC generated')
    lead_id = fields.Many2one('crm.lead')
    sale_id = fields.Many2one('sale.order')

    def _compute_full_cleanning_days(self):
        for rec in self:
            rec.full_cleanning_days = 0
            if rec.establishment_id:
                plants = self.env['res.partner'].search([('type', '=', 'plant'), ('parent_id', '=', rec.establishment_id.id)])
                if plants:
                    rec.full_cleanning_days = sum(plants.mapped('days_plant'))

    # def button_create_lead_related(self):
    #     '''
    #         MOD 07/01--> Genera una nueva oportunidad en estado "Presupuesto Frecuencia" para poder empezar a realizar
    #         el trabajo de este presupuesto, o crea directamente una orden de venta si el valor esperado
    #         es menor a 500.
    #     '''
    #     for rec in self:
    #         if not rec.lead_id:
    #             last_workorder = rec.previous_workorder_id
    #             related_lead = last_workorder.lead_id
    #
    #             # Verificar el expected_revenue del lead relacionado
    #             if related_lead.expected_revenue and related_lead.expected_revenue >= 500:
    #                 # Crear nuevo lead como antes
    #                 stage_frecuency = self.env['crm.stage'].search([('frecuency', '=', True)])
    #                 info = _('Last Workorder: ') + last_workorder.name + _('\nPlants that had been cleaned:\n')
    #                 info_plants = ''
    #                 for p in last_workorder.related_plant_ids:
    #                     info_plants += '    - ' + p.name + '\n'
    #                 info += info_plants
    #
    #                 lead_data = {
    #                     'name': _('Lead created by Frecuency - ') + rec.establishment_id.name,
    #                     'partner_id': rec.establishment_id.id,
    #                     'plant_ids': last_workorder.related_plant_ids.ids,
    #                     'type': 'opportunity',
    #                     'stage_id': stage_frecuency.id,
    #                     'wo_type': 'cleaning',
    #                     'description': info,
    #                     'created_by_frecuency': True,
    #                 }
    #                 new_lead = self.env['crm.lead'].create(lead_data)
    #                 rec.write({
    #                     'lead_id': new_lead.id,
    #                     'status': 'created',
    #                 })
    #             else:
    #                 # Crear directamente una orden de venta
    #                 sale_order_data = {
    #                     'partner_id': rec.establishment_id.id,
    #                     'opportunity_id': related_lead.id,
    #                     'company_id': self.env.company.id,
    #                 }
    #                 new_sale = self.env['sale.order'].create(sale_order_data)
    #                 rec.write({
    #                     'sale_id': new_sale.id,
    #                     'status': 'created',
    #                 })
    #                 # Mostrar mensaje al usuario
    #                 message = _(
    #                     "Se ha creado un presupuesto porque el ingreso esperado de la oportunidad es menor a 500 euros")
    #                 return {
    #                     'type': 'ir.actions.client',
    #                     'tag': 'display_notification',
    #                     'params': {
    #                         'title': _('Presupuesto Creado'),
    #                         'message': message,
    #                         'sticky': True,
    #                         'type': 'success',
    #                         'next': {'type': 'ir.actions.act_window_close'},
    #                     }
    #                 }

    def button_create_lead_related(self):
        '''
            MOD 07/01--> Genera una nueva oportunidad en estado "Presupuesto Frecuencia" para poder empezar a realizar
            el trabajo de este presupuesto, o crea directamente una orden de venta si el valor esperado
            es menor a 500.
            MOD 21/04--> Se quita la funcionalidad de que cree presupuesto (después de 1 mes de prueba borrar la funcion
            comentada arriba)
        '''
        for rec in self:
            if not rec.lead_id:
                last_workorder = rec.previous_workorder_id

                # Crear nuevo lead
                stage_frecuency = self.env['crm.stage'].search([('frecuency', '=', True)])
                info = _('Last Workorder: ') + last_workorder.name + _('\nPlants that had been cleaned:\n')
                info_plants = ''
                for p in last_workorder.related_plant_ids:
                    info_plants += '    - ' + p.name + '\n'
                info += info_plants

                lead_data = {
                    'name': _('Lead created by Frecuency - ') + rec.establishment_id.name,
                    'partner_id': rec.establishment_id.id,
                    'plant_ids': last_workorder.related_plant_ids.ids,
                    'type': 'opportunity',
                    'stage_id': stage_frecuency.id,
                    'wo_type': 'cleaning',
                    'description': info,
                    'created_by_frecuency': True,
                }
                new_lead = self.env['crm.lead'].create(lead_data)
                rec.write({
                    'lead_id': new_lead.id,
                    'status': 'created',
                })

    # def recalculate_dates(self):
    #     for rec in self:
    #         if rec.previous_workorder_id:
    #             rec.write({
    #                 'last_workorder_date': rec.previous_workorder_id.start_date,
    #                 'calculated_date': rec.previous_workorder_id.start_date.date() + timedelta(days=rec.establishment_id.delay),
    #             })

    def recalculate_dates(self):
        for record in self:
            if record.last_workorder_date and record.delay:
                record.calculated_date = record.last_workorder_date + timedelta(days=record.delay)
            else:
                record.calculated_date = False

    def cron_generate_frecuency_leads(self):
        '''
            Acción planificada que se ejecuta solo 1 vez para revisar si se necesita generar un nuevo registro de presupuestos de frecuencia para un establecimiento.
        '''
        frecuency_establishments = self.env['res.partner'].search([('type', '=', 'establishment'), ('frecuency_active', '=', True)])
        for est in frecuency_establishments:
            # Órdenes del establecimiento que tenga algún check a True y que esté finalizada o facturada.
            wo_domain = ['&',
                         ('establishment_id', '=', est.id),
                         '&',
                         ('state', 'in', ['finished', 'invoiced', ]),
                         '|', ('complete_system', '=', True),
                         '|', ('cooker_hood', '=', True),
                         '|', ('duct', '=', True),
                         ('filtronic', '=', True)]

            last_finished_workorder = self.env['work.order.clean'].search(wo_domain, order='end_date DESC', limit=1)
            frec_lead_created = self.env['frecuency.lead'].search([('status', '=', 'current'), ('establishment_id', '=', est.id)])
            workorder_not_finished = self.env['work.order.clean'].search([
                ('establishment_id', '=', est.id),
                '&',
                ('state', 'not in', ['finished', 'invoiced', ]),
                '|', ('complete_system', '=', True),
                '|', ('cooker_hood', '=', True),
                '|', ('duct', '=', True),
                ('filtronic', '=', True)])
            if last_finished_workorder and not workorder_not_finished:
                if not frec_lead_created:
                    frecuency_lead_vals = {
                        'name': _('PENDING FRECUENCY LEAD - ') + est.name,
                        'establishment_id': est.id,
                        'previous_workorder_id': last_finished_workorder.id,
                        'calculated_date': last_finished_workorder.start_date.date() + timedelta(days=est.delay),
                        'last_workorder_date': last_finished_workorder.start_date.date(),
                    }
                    self.env['frecuency.lead'].create(frecuency_lead_vals)
        # Desactivamos la acción planificada para que no se vuelva a ejecutar.
        self.env.ref('onmi_reliex_frecuency_leads.oeng_generate_pending_frecuency_leads_cron').write({'active': False})

    @api.model
    def check_expired_dates(self):
        """
        Función para marcar registros como caducados cuando la fecha calculada es anterior a la fecha actual
        """
        today = fields.Date.today()
        expired_leads = self.search([
            ('status', '=', 'current'),
            ('calculated_date', '<', today)
        ])
        if expired_leads:
            expired_leads.write({'status': 'expired'})
        return True

    @api.model
    def cron_check_expired_frecuency_leads(self):
        """
        Acción planificada para revisar diariamente si hay leads de frecuencia que deben marcarse como expirados.
        """
        return self.check_expired_dates()