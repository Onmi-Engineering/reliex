from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # complete_system = fields.Boolean('Complete system')
    complete_system = fields.Boolean(string='Complete System', compute='_compute_complete_system', store=True)
    cooker_hood = fields.Boolean('Cooker hood')
    duct = fields.Boolean('Duct')
    extractor = fields.Boolean('Extractor')
    filtronic = fields.Boolean('Filtronic')

    establishment_id = fields.Many2one('res.partner')

    make_visible = fields.Boolean(string="User", compute="get_user", default=True)

    establishment_days_of_clean = fields.Integer(
        string='Days of clean',
        # related='partner_id.establishment_days_clean',
        store=True,
        readonly=True
    )

    def get_user(self):
        active_user_id = self.env.user.id
        active_user = self.env['res.users'].search([('id', '=', active_user_id)])
        for x in self:
            if active_user.env.user.has_group('onmi_reliex_operations.otl_editable'):
                x.make_visible = True
            else:
                x.make_visible = False

    def action_quotation_send(self):
        result = super(SaleOrder, self).action_quotation_send()
        for rec in self:
            if rec.opportunity_id:
                if rec.opportunity_id.wo_type == 'cleaning':
                    rec.opportunity_id.stage_id = self.env.ref(
                        'onmi_reliex_contacts.stage_quotation_send_cleaning')
                else:
                    rec.opportunity_id.stage_id = self.env.ref(
                        'onmi_reliex_contacts.stage_quotation_send_new_plant')
        return result

    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        for rec in self:
            if rec.opportunity_id:
                if rec.opportunity_id.wo_type == 'cleaning':
                    rec.opportunity_id.stage_id = self.env.ref(
                        'onmi_reliex_contacts.stage_quotation_accepted_cleaning')
                else:
                    rec.opportunity_id.stage_id = self.env.ref(
                        'onmi_reliex_contacts.stage_quotation_accepted_new_plant')
        return result

    # @api.depends('order_line.product_id.product_tmpl_id.is_system_complete')
    # def _compute_complete_system(self):
    #     for order in self:
    #         order.complete_system = any(
    #             line.product_id.product_tmpl_id.is_system_complete
    #             for line in order.order_line
    #         )

    @api.onchange('order_line')
    def _onchange_order_line_complete_system(self):
        # Calcular complete_system
        product_lines = self.order_line.filtered(lambda l: not l.display_type)
        self.complete_system = any(
            line.product_id.product_tmpl_id.is_system_complete
            for line in product_lines
        )

        # Gestionar la nota
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

        # Buscar por una parte única del texto en lugar del texto completo
        existing_note = self.order_line.filtered(
            lambda l: l.display_type == 'line_note' and '[SERVICIO] Aclaraciones del servicio:' in (l.name or '')
        )

        if self.complete_system and not existing_note:
            # Agregar nota
            new_line = self.env['sale.order.line'].new({
                'display_type': 'line_note',
                'name': note_text,
                'order_id': self.id,
            })
            self.order_line |= new_line
