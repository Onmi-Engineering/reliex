from odoo import fields, models, api, _


class CookerHood(models.Model):
    _inherit = 'cooker.hood'

    # region COOKER HOOD DATA
    cooker_image = fields.Binary("Cooker image")
    cooker_type = fields.Selection([
        ('island', 'Island'),
        ('wall', 'Wall')], string='Type')
    material = fields.Selection([
        ('inox', 'Inox'),
        ('galvan', 'Galva'),
        ('inox_galvan0', 'Outdoor Inox / Indoor Galva')], string='Material')
    cooker_dimmensions = fields.Char('Dimmensions')
    faces = fields.Selection([
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4')], string="Caras abiertas")
    plenum = fields.Boolean('Take plenum')
    fire_protection = fields.Boolean('Fire protection')
    waterproof_luminaire = fields.Boolean('Waterproof luminaire')
    material_filter = fields.Selection([
        ('inox', 'Inox'),
        ('galvan', 'Galva'),
        ('active_carbon', 'Active carbon')], string='Filters Materials')

    cooker_comments = fields.Text('Comments')

    # endregion

    # region DUCT DATA
    ei30 = fields.Boolean('With EI30')
    round = fields.Boolean('Round')
    square = fields.Boolean('Square')
    dimmensions_diameter = fields.Char('Dimmensions Ø')
    dimmensions_square = fields.Char('Dimmensions □')
    duct_type = fields.Selection([
        ('lock', 'Lock'),
        ('plate', 'Plate'),
        ('insulated_plate', 'Insulated plate'),
        ('double_insulated_plate', 'Double insulated plate'),
        ('fibre', 'Fibre'),
        ('flexible', 'Flexible')], string='Type')
    duct_location = fields.Selection([
        ('sun', 'Sun'),
        ('terrace', 'Terrace'),
        ('facade', 'Facade'),
        ('other', 'Other')], string='Location of vertical')
    height_on_floor = fields.Float("Height on floor (meters)")
    duct_leaks = fields.Boolean('Duct leaks')
    install_registers = fields.Boolean('Install registers')
    vertical_meters = fields.Float('Vertical meters')
    horizontal_meters = fields.Float('Horizontal meters')
    soiling_degree_duct = fields.Selection([
        ('0', 'None'),
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High'),
        ('4', 'Very High'),
        ('5', 'Highest'),
    ], string='Degree of soiling', )
    demountable_roof = fields.Boolean('Demountable roof?')
    do_registers = fields.Boolean('Do registers on fixed roof')
    hydraulic_machine = fields.Boolean('Hydraulic machine?')
    manually_machine = fields.Boolean('Manually machine?')
    noise_problems = fields.Boolean('Noise problems?')
    duct_register_ids = fields.One2many('duct.register', 'cooker_id', string='Duct registers')
    duct_ref = fields.Char('Duct Ref')

    duct_comments = fields.Text('Duct comments')
    # endregion

    # region EXTRACTOR DATA
    shape = fields.Selection([
        ('round', 'Round'),
        ('rectangular', 'Rectangular'),
        ('square', 'Square')], string='Shape')

    model_and_brand = fields.Char('Model and brand')
    extractor_type = fields.Selection([
        ('centrifugal', 'Centrifugal'),
        ('helicoidal', 'Helicoidal')], string='Type')
    extractor_transmission = fields.Selection([
        ('direct', 'Direct'),
        ('pulley', 'Pulley')], string='Transmission')
    extractor_ref = fields.Char(string='Reference', index=True)
    extractor_image = fields.Binary("Identification plate")
    vibration = fields.Boolean('Vibration')
    neighbor_noise = fields.Boolean('Noise to neighbors')
    bearing_noise = fields.Boolean('Bearing noise')
    bearing_ref = fields.Char('Bearing reference')

    substitute_belt = fields.Boolean('Substitute belts?')
    belt_ref = fields.Char('Belt ref')
    belt_ref_image = fields.Binary('Belt reference')
    extractor_height_on_floor = fields.Float("Height on floor (meters)")
    grease_leaks = fields.Boolean('Grease leaks')
    antivibration_gasket = fields.Boolean('Anti-vibration gasket')
    place_tray = fields.Boolean('Place tray')
    place_sineblocks = fields.Boolean('Place sineblocks')
    clean_extractor = fields.Boolean('Clean extractor area')
    plug = fields.Boolean('Plug')
    box_dimmensions = fields.Char('Box dimmensions')
    has_water_intake = fields.Boolean('Has water intake?')
    has_power_supply = fields.Boolean('Has power supply?')

    extractor_location = fields.Selection([
        ('attic', 'Attic'),
        ('false_ceiling', 'False Ceiling'),
        ('rooftop', 'Rooftop'),
        ('other', 'Other')], string='Location')
    location_image = fields.Binary('Location')
    extractor_soiling_degree = fields.Selection([
        ('0', 'None'),
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High'),
        ('4', 'Very High'),
        ('5', 'Highest'),
    ], string='Degree of soiling')

    epis = fields.Boolean('EPIS high work')
    extractor_comments = fields.Text('Extractor comments')
    # endregion

    # region FILTRONIC
    filtronic_cleaning = fields.Boolean('Filtronic cleaning')
    full_cleaning = fields.Boolean('Full cleaning')
    electrostatic_filter_cleaning = fields.Boolean('Electrostatic filter cleaning')
    active_carbon_filter_replacement = fields.Boolean('Active carbon filter replacement')
    filtrina_replacement = fields.Boolean('Filtrina replacement')
    filtronic_comments = fields.Text('Filtronic comments')
    # endregion
