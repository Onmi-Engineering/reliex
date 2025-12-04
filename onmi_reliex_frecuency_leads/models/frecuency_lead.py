from odoo import fields, models, api, _
from odoo.exceptions import UserError
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
    #     for rec in self:
    #         if not rec.lead_id:
    #             last_workorder = rec.previous_workorder_id
    #             related_lead = last_workorder.lead_id
    #
    #             sale_order_data = {
    #                 'partner_id': rec.establishment_id.id,
    #                 'opportunity_id': related_lead.id,
    #                 'company_id': self.env.company.id,
    #             }
    #             new_sale = self.env['sale.order'].create(sale_order_data)
    #             rec.write({
    #                 'sale_id': new_sale.id,
    #                 'status': 'created',
    #             })
    #             # Mostrar mensaje al usuario
    #             message = _(
    #                 "Se ha creado un presupuesto por frecuencia")
    #             return {
    #                 'type': 'ir.actions.client',
    #                 'tag': 'display_notification',
    #                 'params': {
    #                     'title': _('Presupuesto Creado'),
    #                     'message': message,
    #                     'sticky': True,
    #                     'type': 'success',
    #                     'next': {'type': 'ir.actions.act_window_close'},
    #                 }
    #                 }

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


    def button_create_lead_related(self):
        for rec in self:
            if not rec.lead_id:
                last_workorder = rec.previous_workorder_id
                related_lead = last_workorder.lead_id

                # Obtener la lista de precios por defecto o la del cliente
                pricelist = self.establishment_id.property_product_pricelist or self.env['product.pricelist'].search([],
                                                                                                                     limit=1)
                client_partner = self.establishment_id.parent_id

                sale_order_vals = {
                    'partner_id': client_partner.id,  # Cliente principal
                    'partner_shipping_id': self.establishment_id.id,  # Establecimiento como dirección de entrega
                    'partner_invoice_id': client_partner.id,
                    'complete_system': True,
                    'cooker_hood': last_workorder.cooker_hood,
                    'duct': last_workorder.duct,
                    'opportunity_wo_type': 'cleaning',
                    'wo_clean_origin': last_workorder.id,
                    'extractor': last_workorder.extractor,
                    'filtronic': last_workorder.filtronic,
                    'date_order': fields.Datetime.now(),
                    'pricelist_id': pricelist.id,
                    'origin': last_workorder.name,  # Referencia a la orden de trabajo
                    'user_id': client_partner.user_id.id if client_partner.user_id else False,
                    # Usuario desde el cliente
                    'note': _('Presupuesto generado automáticamente desde OTL: %s\n'
                              'Fecha del servicio: %s\n'
                              'Sistema completo realizado.') % (last_workorder.name, last_workorder.start_date.date()),
                }

                new_sale_order = self.env['sale.order'].create(sale_order_vals)

                # Buscar el producto con is_system_complete = True
                system_complete_product = self.env['product.product'].search([
                    ('is_system_complete', '=', True)
                ], limit=1)

                if system_complete_product:
                    # Crear la línea del pedido con el producto de sistema completo
                    line_vals = {
                        'order_id': new_sale_order.id,
                        'product_id': system_complete_product.id,
                        'name': system_complete_product.display_name,
                        'product_uom_qty': 1,
                        'product_uom': system_complete_product.uom_id.id,
                        'price_unit': system_complete_product.list_price,
                        'tax_id': [(6, 0, system_complete_product.taxes_id.ids)],
                    }

                    # Crear la línea del pedido
                    self.env['sale.order.line'].create(line_vals)

                    # Agregar nota de servicio si no existe ya
                    note_text = ("[SERVICIO] Aclaraciones del servicio:\n"
                                 "-Equipo humano formado por dos técnicos, con amplia experiencia y formación.\n"
                                 "-Equipos mecánicos adaptados para este tipo instalaciones.\n"
                                 "-Limpieza de conductos realizada con cepillado neumático, siempre que sea la opción más óptima.*\n"
                                 "-Espuma activa desengrasante.\n"
                                 "-Plastificado de todas las zonas susceptibles a mancharse.\n"
                                 "-Certificado administrativo de la limpieza.\n"
                                 "-Subsanación in situ de cualquier deficiencia relacionada con el Sistema de extracción de humos (siempre que sea posible) y, en caso de no ser posible, valoración de la misma para su posterior reparación.\n"
                                 "-Queda excluida la limpieza de los filtros de la/s campana/s.\n"
                                 "-Verificación post venta de la calidad del servicio.")

                    # Verificar si ya existe una nota con este contenido
                    existing_note = new_sale_order.order_line.filtered(
                        lambda l: l.display_type == 'line_note' and '[SERVICIO] Aclaraciones del servicio:' in (
                                    l.name or '')
                    )

                    # Si no existe, crear la línea de nota
                    if not existing_note:
                        note_vals = {
                            'order_id': new_sale_order.id,
                            'display_type': 'line_note',
                            'name': note_text,
                            'sequence': 9999,  # Para que aparezca al final
                        }
                        self.env['sale.order.line'].create(note_vals)

                else:
                    raise UserError(_('No se encontró ningún producto con "Sistema Completo" activado. '
                                      'Por favor, configure un producto con el campo is_system_complete = True.'))

                # Mensaje para notificación
                message = _(
                    "Se ha creado un nuevo presupuesto: %s para el cliente %s") % (
                              new_sale_order.name,
                              new_sale_order.partner_id.name
                          )

                notification = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('PRESUPUESTO CREADO'),
                        'message': message,
                        'sticky': True,
                        'type': 'success',
                        'next': {'type': 'ir.actions.act_window_close'},
                        'messageIsHtml': True
                    }
                }

                # Retornar notificación si existe
            if notification:
                return notification