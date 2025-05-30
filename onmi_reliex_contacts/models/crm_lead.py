from odoo import fields, models, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError

from datetime import timedelta


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    wo_type = fields.Selection([('cleaning', 'Cleaning'), ('new_plant', 'New Plant')], 'WO Type', required=True)

    plant_ids = fields.Many2many('res.partner', domain=[('type', '=', 'plant')], string='Plants')
    incident_opened_count = fields.Integer('Incident opened', compute='_compute_incident_opened_count', store=False)
    created_by_frecuency = fields.Boolean('Create by frecuency')
    work_notes = fields.Html('Work notes')

    def _compute_incident_opened_count(self):
        for rec in self:
            rec.incident_opened_count = self.env['incident'].search_count(
                [('plant_id', 'in', rec.plant_ids.ids), ('incident_type', '=', 'reliex_info'),
                 ('state', '=', 'handling')])

    def action_show_incident_opened(self):
        action = self.env["ir.actions.actions"]._for_xml_id("onmi_reliex_operations.onmi_action_incident")
        action['domain'] = [('plant_id', 'in', self.plant_ids.ids), ('incident_type', '=', 'reliex_info'),
                            ('state', '=', 'handling')]
        action['context'] = {
            'create': 0,
        }
        return action

    def action_show_incident_related(self):
        action = self.env["ir.actions.actions"]._for_xml_id("onmi_reliex_operations.onmi_action_incident")
        action['domain'] = [('plant_id', 'in', self.plant_ids.ids)]
        action['context'] = {
            'create': 0,
        }
        return action

    @api.onchange('stage_id')
    def check_stage(self):
        for rec in self:
            if rec.stage_id.sequence >= 4 and not rec.plant_ids and rec.wo_type == 'cleaning':
                raise UserError(_('You have to indicate plants to clean.'))
            if rec.stage_id.sequence >= 4:
                raise UserError(_('You can´t change this values of stage. Please, follow the workflow.'))

    def action_material_list(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("onmi_reliex_operations.material_list_leads_act_window")
        action['domain'] = [('lead_id', '=', self.id)]
        action['view_mode'] = 'tree,form'
        action['context'] = {
            'create': False
        }
        return action

    def action_create_material_list(self):
        if self.partner_id.parent_id.fictitious_customer:
            raise UserError(_('You can´t create a material list with a establishment from a ficticious partner.\n'
                              'Please, change its parent partner to continue creating quotation.'))
        action = self.env["ir.actions.actions"]._for_xml_id("onmi_reliex_operations.material_list_act_window")
        action['domain'] = [('establishment_id', '=', self.partner_id.id)]
        action['view_mode'] = 'form'
        action['target'] = 'current'
        action['context'] = {'default_establishment_id': self.partner_id.id, 'default_lead_id': self.id}
        return action


    def action_set_won_rainbowman(self):
        res = super(CrmLead, self).action_set_won_rainbowman()
        # LIMITAR BOTÓN 'GANADO' PARA ADMINISTRADORES DE LIMPIEZA y/o INSTALACIÓN
        total_days = False
        if not self.env.user.has_group(
                'onmi_reliex_operations.group_operation_administrator_plant') or not self.env.user.has_group(
            'onmi_reliex_operations.group_operation_administrator_cleaning'):
            raise UserError(_('Sorry, You dont have permissions to do this action.'))
        # No se puede marcar como Ganado si no hay instalaciones indicadas.
        if not self.plant_ids:
            raise UserError(_('Sorry, You have to fill plants for this lead to mark as win.'))
        # No se puede marcar como Ganado si no hay / hay un pedido confirmado para esta oportunidad.
        sale_orders = self.env['sale.order'].search_count([('opportunity_id', '=', self.id), ('state', '=', 'sale')])
        if sale_orders == 0:
            raise UserError(_('Sorry, You have to have a sale order related with this lead to mark as win.\n'
                              'Please, create a new one or confirm which exists.'))

        list_material = self.env['material.list'].search([('lead_id', '=', self.id)])
        # region SIGUIENTE LUNES
        # day_start = self.next_monday()
        # endregion

        if not self.wo_type:
            raise UserError(_('Yo have to indicate type ( Cleaning or Plant)'))
        plants = self.env['res.partner'].search(
            [('parent_id', '=', self.partner_id.id), ('type', '=', 'plant')])
        '''
                LIMPIEZA: Genera OTL por establecimiento y PTL por instalación y días de limpieza.
        '''
        # if self.wo_type == 'cleaning':
        #     wo_clean = self.env['work.order.clean'].sudo().create({
        #         'name': _('New'),
        #         'partner_id': self.partner_id.parent_id.id,
        #         'establishment_id': self.partner_id.id,
        #         'related_plant_ids': self.plant_ids.ids,
        #         'lead_id': self.id,
        #         'user_id': self.user_id.id,
        #         'complete_system': self.order_ids.filtered(lambda o: o.state == 'sale')[0].complete_system,
        #         'cooker_hood': self.order_ids.filtered(lambda o: o.state == 'sale')[0].cooker_hood,
        #         'duct': self.order_ids.filtered(lambda o: o.state == 'sale')[0].duct,
        #         'extractor': self.order_ids.filtered(lambda o: o.state == 'sale')[0].extractor,
        #         'filtronic': self.order_ids.filtered(lambda o: o.state == 'sale')[0].filtronic,
        #     })
        if self.wo_type == 'cleaning':
            # Crear un diccionario con los valores base
            wo_clean_vals = {
                'name': _('New'),
                'partner_id': self.partner_id.parent_id.id,
                'establishment_id': self.partner_id.id,
                'related_plant_ids': self.plant_ids.ids,
                'lead_id': self.id,
                'user_id': self.user_id.id,
                'complete_system': self.order_ids.filtered(lambda o: o.state == 'sale')[0].complete_system,
                'cooker_hood': self.order_ids.filtered(lambda o: o.state == 'sale')[0].cooker_hood,
                'duct': self.order_ids.filtered(lambda o: o.state == 'sale')[0].duct,
                'extractor': self.order_ids.filtered(lambda o: o.state == 'sale')[0].extractor,
                'filtronic': self.order_ids.filtered(lambda o: o.state == 'sale')[0].filtronic,
            }

            # Añadido para indicar el campo wo_created_by_incident si created_by_incident es True
            if hasattr(self, 'created_by_incident') and self.created_by_incident:
                wo_clean_vals['wo_created_by_incident'] = True

            # Crear el registro con todos los valores
            wo_clean = self.env['work.order.clean'].sudo().create(wo_clean_vals)

            # Generar líneas de recursos asociadas a wo_clean = líneas de presupuesto.
            lines = self.env['materials']
            '''
            Se agrega esto para poder transportar las notas y secciones del presupuesto a OTL y partes abajo
            esta el codigo original comentado *1   
            '''
            # for sale_line in self.order_ids.filtered(lambda so: so.state == 'sale').order_line:
            #     if sale_line.display_type in ('line_section', 'line_note'):
            #         # Agregar las líneas de sección y nota a la orden de trabajo de limpieza
            #         wo_clean.sudo().write({
            #             'line_ids': [(0, 0, {
            #                 'name': sale_line.name,  # Usar el nombre para estas líneas
            #                 'display_type': sale_line.display_type,
            #                 'wo_clean_id': wo_clean.id,
            #                 'sale_order_line_id': sale_line.id
            #             })]
            #         })
            #     else:
            #         # Manejar líneas de productos normales
            #         wo_clean.sudo().write({
            #             'line_ids': [(0, 0, {
            #                 'product_id': sale_line.product_id.id,
            #                 'quantity': sale_line.product_uom_qty,
            #                 'wo_clean_id': wo_clean.id,
            #                 'sale_order_line_id': sale_line.id
            #             })]
            #         })
            #         lines += self.env['materials'].sudo().create({
            #             'product_id': sale_line.product_id.id,
            #             'quantity': sale_line.product_uom_qty,
            #             'sale_order_line_id': sale_line.id,
            #         })
            # CODIGO ORIGINAL *1
            for sale_line in self.order_ids.filtered(lambda so: so.state == 'sale').order_line.filtered(
                    lambda ol: ol.display_type != 'line_section' and ol.display_type != 'line_note'):
                wo_clean.sudo().write({
                    'line_ids': [(0, 0, {
                        'product_id': sale_line.product_id.id,
                        'quantity': sale_line.product_uom_qty,
                        'wo_clean_id': wo_clean.id,
                        'sale_order_line_id': sale_line.id})]
                })
                lines += self.env['materials'].sudo().create({
                    'product_id': sale_line.product_id.id,
                    'quantity': sale_line.product_uom_qty,
                    'sale_order_line_id': sale_line.id,
                })
            if plants:
                for plant in self.plant_ids:
                    total_days = 0
                    total_days += plant.days_clean
                    for day in range(total_days):
                        part = self.env['worksheet.part'].sudo().create({
                            'name': _('New'),
                            'partner_id': self.partner_id.parent_id.id,
                            'establishment_id': self.partner_id.id,
                            'plant_id': plant.id,
                            'workorder_id': wo_clean.id,
                            'part_type': 'cleaning',
                            'allday': True,
                            'user_id': self.user_id.id,
                        })
                        for line in lines:
                            part.sudo().write({'cleaning_line_ids': [(0, 0, {
                                'product_id': line.product_id.id,
                                'sale_order_line_id': line.sale_order_line_id.id,
                                'worksheet_id': part.id
                            })]})
            self.stage_id = self.env['crm.stage'].search([('is_won', '=', True), ('type', '=', 'cleaning')])
        '''
            INSTALACIÓN: Crea OTI por instalación con recursos totales de la instalación + PTI por días de instalación totales
            con todos los recursos añadidos pero sin uds.
        '''
        if self.wo_type == 'new_plant':
            materials = self.env['materials'].sudo().search([('list_id', '=', list_material.id)])
            purchase_orders = self.env['purchase.order'].search([
                ('opportunity_id', '=', self.id),
                ('origin', '=', self.name),
                ('po_selected', '=', True),
            ])
            purchase_lines = purchase_orders.order_line

            if self.plant_ids:
                first_part = False
                workorders = self.env['work.order.plant']
                worksheets = self.env['worksheet.part']
                for plant in self.plant_ids:
                    wo_plant = self.env['work.order.plant'].sudo().create({
                        'name': _('New'),
                        'partner_id': self.partner_id.parent_id.id,
                        'establishment_id': self.partner_id.id,
                        'plant_id': plant.id,
                        'start_date': fields.Datetime.now(),
                        'end_date': fields.Datetime.now() + timedelta(minutes=30),
                        'lead_id': self.id,
                        'user_id': self.user_id.id,
                    })
                    workorders |= wo_plant
                    wo_plant.line_ids = materials.filtered(lambda mat: mat.plant_id.id == plant.id)
                    for line in wo_plant.line_ids:
                        purchase_line_product = purchase_lines.filtered(lambda l: l.product_id.id == line.product_id.id)
                        line.write({
                            'supplier_id': purchase_line_product[0].order_id.partner_id.id,
                        })
                        purchase_lines -= purchase_line_product
                    for rec in range(plant.days_plant):
                        if first_part == False:
                            # worksheet = self.env['worksheet.part'].sudo().create({
                            #     'name': _('New'),
                            #     'partner_id': self.partner_id.parent_id.id,
                            #     'establishment_id': self.partner_id.id,
                            #     'part_type': 'plant',
                            #     'start_date': day_init + timedelta(days=rec),
                            #     'end_date': day_init + timedelta(days=rec) + timedelta(hours=1),
                            #     'allday': True,
                            #     'user_id': self.user_id.id,
                            #     'first_part': True,
                            # })
                            worksheet = self.env['worksheet.part'].sudo().create({
                                'name': _('New'),
                                'partner_id': self.partner_id.parent_id.id,
                                'establishment_id': self.partner_id.id,
                                'part_type': 'plant',
                                'allday': False,
                                'user_id': self.user_id.id,
                                'first_part': True,
                            })
                            first_part = True
                        else:
                            # worksheet = self.env['worksheet.part'].sudo().create({
                            #     'name': _('New'),
                            #     'partner_id': self.partner_id.parent_id.id,
                            #     'establishment_id': self.partner_id.id,
                            #     'workorder_plant_id': wo_plant.id,
                            #     'part_type': 'plant',
                            #     'start_date': day_init + timedelta(days=rec),
                            #     'end_date': day_init + timedelta(days=rec) + timedelta(hours=1),
                            #     'allday': True,
                            #     'user_id': self.user_id.id,
                            # })
                            worksheet = self.env['worksheet.part'].sudo().create({
                                'name': _('New'),
                                'partner_id': self.partner_id.parent_id.id,
                                'establishment_id': self.partner_id.id,
                                'workorder_plant_id': wo_plant.id,
                                'part_type': 'plant',
                                'allday': True,
                                'user_id': self.user_id.id,
                            })
                        for mat in materials:
                            worksheet.sudo().write({'line_ids': [(0, 0, {
                                'product_id': mat.product_id.id,
                                'plant_id': mat.plant_id.id,
                            })]})

                        worksheets |= worksheet
                workorders.sudo().write({'worksheet_ids': worksheets})
                worksheets.sudo().write({'workorder_ids': workorders})

            self.stage_id = self.env['crm.stage'].search([('is_won', '=', True), ('type', '=', 'new_plant')])
        return res

    def action_sale_quotations_new(self):
        action = super(CrmLead, self).action_sale_quotations_new()
        if self.partner_id.parent_id.fictitious_customer:
            raise UserError(_('You can´t create a quotation with a establishment from a ficticious partner.\n'
                              'Please, change its parent partner to continue creating quotation.'))
        if not self.plant_ids:
            raise UserError(_('You can´t create a quotation without plants assigned.\n'
                              'Please, fill it to create a quotation.'))
        if not self.partner_id and not self.plant_ids:
            raise UserError(_("You have to fill establishment and plants to create a quotation."))
        else:
            action['context'] = {
                'default_partner_id': self.partner_id.parent_id.id,
                'default_establishment_id': self.partner_id.id,
                'search_default_opportunity_id': self.id,
                'default_opportunity_id': self.id,
                'search_default_partner_id': self.partner_id.parent_id.id,
                'default_campaign_id': self.campaign_id.id,
                'default_medium_id': self.medium_id.id,
                'default_origin': self.name,
                'default_source_id': self.source_id.id,
                'default_company_id': self.company_id.id or self.env.company.id,
                'default_tag_ids': [(6, 0, self.tag_ids.ids)],
                'default_establishment_days_of_clean': self.partner_id.establishment_days_clean,
            }
            return action

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        res = super(CrmLead, self)._read_group_stage_ids(stages, domain, order)

        if self._context.get('default_wo_type') == 'new_plant':
            search_domain = [('type', '=', 'new_plant'), ('team_id', '=', False)]
            stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
            return stages.browse(stage_ids)
        if self._context.get('default_wo_type') == 'cleaning':
            search_domain = [('type', '=', 'cleaning'), ('team_id', '=', False)]
            stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
            return stages.browse(stage_ids)
        return res
