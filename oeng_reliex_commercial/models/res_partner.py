from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # region ESTABLISHMENT DATA
    clean_filtronic = fields.Boolean('Clean Filtronic')
    clean_solar_panel = fields.Boolean('Clean solar panel')
    clean_sink = fields.Boolean('Clean sink')
    clean_terrace = fields.Boolean('Clean terrace')
    clean_by_external = fields.Boolean('Window cleaning by an external company')
    ex_company_name = fields.Char('External company name')
    grease_separator_cleaning = fields.Boolean('Grease separator cleaning')
    ex_company_name_oil = fields.Char('Name of used oil management company')
    establishment_days_clean = fields.Integer('Total days cleaning', compute='_compute_establishment_days_clean')
    establishment_days_plant = fields.Integer('Total days plant', compute='_compute_establishment_days_plant')
    woc_count = fields.Integer('WOC count', compute="_compute_woc_count")
    wop_count = fields.Integer('WOC count', compute="_compute_wop_count")

    # endregion
    # region PLANT DATA
    total_days_clean = fields.Integer('Necessary days of cleaning')
    days_clean = fields.Integer('Contracted days of cleaning')
    days_plant = fields.Integer('Days on plant')
    audit_notes = fields.Html('Audit notes')
    # endregion

    def _compute_woc_count(self):
        for rec in self:
            rec.woc_count = self.env['work.order.clean'].sudo().search_count([('establishment_id', '=', rec.id)])

    def _compute_wop_count(self):
        for rec in self:
            rec.wop_count = self.env['work.order.plant'].sudo().search_count([('establishment_id', '=', rec.id)])

    def _compute_establishment_days_clean(self):
        for rec in self:
            if rec.type == 'establishment':
                domain_plant = [('type', '=', 'plant'), ('parent_id', '=', rec.id)]
                rec.establishment_days_clean = sum(self.env['res.partner'].search(domain_plant).mapped('days_clean'))
            else:
                rec.establishment_days_clean = False

    def _compute_establishment_days_plant(self):
        for rec in self:
            if rec.type == 'establishment':
                domain_plant = [('type', '=', 'plant'), ('parent_id', '=', rec.id)]
                rec.establishment_days_plant = sum(self.env['res.partner'].search(domain_plant).mapped('days_plant'))
            else:
                rec.establishment_days_plant = False

    def action_view_duct_registers(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "oeng_reliex_commercial.duct_register_act_window")
        action['domain'] = [('plant_id', '=', self.id)]
        return action

    def cron_assign_new_duct_and_extractor_data(self):
        plants = self.env['res.partner'].search([('type', '=', 'plant')])
        for plant in plants:
            if plant.duct_ids:
                duct_number = 0
                for duct in plant.duct_ids:
                    if len(plant.cooker_hood_ids) > duct_number:
                        plant.cooker_hood_ids[duct_number].write({
                            'duct_ref': duct.ref,
                            'ei30': duct.ei30,
                            'round': duct.round,
                            'square': duct.square,
                            'dimmensions_diameter': duct.dimmensions_diameter,
                            'dimmensions_square': duct.dimmensions_square,
                            'duct_type': duct.type,
                            'duct_location': duct.location,
                            'vertical_meters': duct.vertical_meters,
                            'horizontal_meters': duct.horizontal_meters,
                            'soiling_degree_duct': duct.soiling_degree,
                            'demountable_roof': duct.demountable_roof,
                            'hydraulic_machine': duct.hydraulic_machine,
                            'manually_machine': duct.manually_machine,
                            'noise_problems': duct.noise_problems,
                            'duct_comments': duct.comments,
                        })
                    duct_number += 1
            if plant.extractor_ids:
                extractor_number = 0
                for extractor in plant.extractor_ids:
                    if len(plant.cooker_hood_ids) > extractor_number:
                        plant.cooker_hood_ids[extractor_number].write({
                            'shape': extractor.shape,
                            'model_and_brand': extractor.model_and_brand,
                            'extractor_type': extractor.type,
                            'extractor_transmission': extractor.transmission,
                            'extractor_ref': extractor.ref,
                            'neighbor_noise': extractor.noise,
                            'substitute_belt': extractor.substitute_belt,
                            'belt_ref': extractor.belt_ref,
                            'has_water_intake': extractor.has_water_intake,
                            'has_power_supply': extractor.has_power_supply,
                            'extractor_location': extractor.locations,
                            'extractor_soiling_degree': extractor.soiling_degree,
                            'epis': extractor.epis,
                            'extractor_comments': extractor.comments,
                        })
                    extractor_number += 1

    def action_view_woc(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("onmi_reliex_operations.onmi_action_work_order_clean_full")
        action['domain'] = [
            ('establishment_id', 'in', self.ids),
        ]
        action['context'] = {'default_establishment_id': self.id, }
        return action

    def action_view_wop(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("onmi_reliex_operations.onmi_action_work_order_plant_full")
        action['domain'] = [
            ('establishment_id', 'in', self.ids),
        ]
        action['context'] = {'default_establishment_id': self.id, }
        return action

    def copy(self, default=None):
        if self.cooker_hood_ids:
            new_cookers = self.cooker_hood_ids.copy()
        res = super(ResPartner, self).copy(default)
        res.write({'cooker_hood_ids': new_cookers})
        return res
