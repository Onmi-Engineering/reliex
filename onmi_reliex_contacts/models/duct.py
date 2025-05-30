from odoo import fields, models, api


class Duct(models.Model):
    _name = 'duct'
    _description = 'Ducts'

    name = fields.Char('Duct name')
    ref = fields.Char(string='Reference', index=True)
    plant_id = fields.Many2one('res.partner')

    round = fields.Boolean('Round')

    ei30 = fields.Boolean('With EI30')

    square = fields.Boolean('Square')

    shape = fields.Selection([
        ('round', 'Round'),
        ('rectangular', 'Rectangular'),
        ('square', 'Square')], string='Shape')

    dimmensions_diameter = fields.Char('Dimmensions Ø')

    dimmensions_square = fields.Char('Dimmensions □')

    type = fields.Selection([
        ('plate', 'Plate'),
        ('ei30', 'EI30'),
        ('insulated_plate', 'Insulated plate'),
        ('double_insulated_plate', 'Double insulated plate'),
        ('fibre', 'Fibre'),
        ('flexible', 'Flexible')], string='Type')

    do_registers = fields.Boolean('Do registers')
    register_qty_round = fields.Integer('Register qty Ø')
    register_qty_squared = fields.Integer('Register qty □')

    vertical_meters = fields.Float('Vertical meters')

    horizontal_meters = fields.Float('Horizontal meters')

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
    demountable_roof = fields.Boolean('Demountable roof?')
    hydraulic_machine = fields.Boolean('Hydraulic machine?')
    manually_machine = fields.Boolean('Manually machine?')
    noise_problems = fields.Boolean('Noise problems?')

    comments = fields.Text('Comments')
