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




    @api.depends('order_line.product_id.product_tmpl_id.is_system_complete')
    def _compute_complete_system(self):
        for order in self:
            order.complete_system = any(
                line.product_id.product_tmpl_id.is_system_complete
                for line in order.order_line
            )