from odoo import fields, models, api


class CookerHood(models.Model):
    _name = 'cooker.hood'
    _description = 'Cooker Hoods'
    _parent_name = "plant_id"

    name = fields.Char('Cooker hood name')
    ref = fields.Char(string='Reference', index=True)
    plant_id = fields.Many2one('res.partner')

    plenum = fields.Boolean('Plenum')

    material = fields.Selection([
        ('inox', 'Inox'),
        ('galvan', 'Galvan'),
        ('inox_galvan0', 'Exterior Inox / Interior Galvanizado')], string='Material')
    location = fields.Selection([
        ('wall', 'Wall'),
        ('central', 'Central')], string='Type')

    soiling_degree = fields.Selection([
        ('0', 'None'),
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High'),
        ('4', 'Very High'),
        ('5', 'Highest'),
    ], string='Degree of soiling',
    )
    number_filters = fields.Integer('# Filters')

    material_filter = fields.Selection([
        ('inox', 'Inox'),
        ('galvan', 'Galvan')], string='Filters Materials')

    location_filter = fields.Selection([
        ('lamas', 'Lamas'),
        ('malla', 'Malla')], string='Filters Type')

    dimmensions = fields.Selection([
        ('49_35', '490x350'),
        ('49_49', '490x490'),
        ('other', 'Other')], string='Filters Dimmensions')

    cleaning_filters = fields.Boolean('Cleaning of filters?')
    comments = fields.Text('Comments')
