from odoo import fields, models, api


class Extractor(models.Model):
    _name = 'extractor'
    _description = 'Extractors'

    name = fields.Char('Extractor name')
    ref = fields.Char(string='Reference', index=True)
    plant_id = fields.Many2one('res.partner')

    locations = fields.Selection([
        ('attic', 'Attic'),
        ('false_ceiling', 'False Ceiling'),
        ('rooftop', 'Rooftop'),
        ('other', 'Other')], string='Location')
    shape = fields.Selection([
        ('round', 'Round'),
        ('rectangular', 'Rectangular'),
        ('square', 'Square')], string='Shape')

    model_and_brand = fields.Char('Model and brand')

    belt_ref = fields.Char('Belt ref')

    substitute_belt = fields.Boolean('Substitute belts?')

    do_registers = fields.Boolean('Do registers')
    register_installed = fields.Char('Register installed')


    has_power_supply = fields.Boolean('Has power supply?')
    has_water_intake = fields.Boolean('Has water intake?')
    take_harness = fields.Boolean('Take harness?')
    take_lifeline = fields.Boolean('Take Lifeline?')
    noise = fields.Boolean('Noise?')

    type = fields.Selection([
        ('centrifugal', 'Centrifugal'),
        ('helicoidal', 'Helicoidal')], string='Type')
    transmission = fields.Selection([
        ('direct', 'Direct'),
        ('pulley', 'Pulley')], string='Transmission')
    register_qty = fields.Integer('Register qty')
    register_dimmensions = fields.Char('Register dimmensions')

    location = fields.Selection([
        ('sun', 'Sun'),
        ('terrace', 'Terrace'),
        ('facade', 'Facade'),
        ('other', 'Other')], string='Location')

    soiling_degree = fields.Selection([
        ('0', 'None'),
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High'),
        ('4', 'Very High'),
        ('5', 'Highest'),
    ], string='Degree of soiling',
    )
    epis = fields.Boolean('EPIS high work')
    comments = fields.Text('Comments')
