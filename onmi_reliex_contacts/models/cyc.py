from odoo import fields, models, api


class InsuranceCaution(models.Model):
    _name = 'insurance.caution'
    _description = 'Insurance Caution CYC'


    cyc_partner_name = fields.Char('Partner Name')
    cyc_vat_number = fields.Char('VAT Number')
    cyc_number = fields.Integer(string='CYC Number')
    policy = fields.Integer(string='Policy Number')

    section = fields.Selection([
        ('aut', 'AUTOMOCIÓN'),
        ('cyp', 'CONSTRUCCIÓN Y PROMOCIÓN'),
        ('cyd', 'COSMÉTICA Y DROGUERÍA'),
        ('dist', 'DISTRIBUCIÓN'),
        ('inst', 'INSTALACIONES'),
        ('mym', 'MADERAS - MUEBLES'),
        ('maq', 'MAQUINARIA INDUSTRIAL'),
        ('tral', 'TRANSFORMACIÓN ALIMENTARIA'),
        ('tyh', 'TURISMO Y HOSTELERÍA'),
        ('sid', 'SIDERÚRGICO'),
        ('pend', 'PENDIENTE DE ASIGNACIÓN'),
        ('otr', 'OTROS SERVICIOS'),
    ], string='Section')

    state = fields.Selection([
        ('vig', 'Vigor'),
        ('lim', 'Limitada nada - rehusada')
    ])

    proposed_date = fields.Date('Date Proposal')
    amount_requested = fields.Float('Amount Requested')
    amount_granted = fields.Float('Amount Granted')
    notes = fields.Text('Notes')
    duration = fields.Integer('Duration up to(days)')
    reason = fields.Text('Reason')
    cancellation_date = fields.Date('Cancellation Date')
    cyc_vat = fields.Char('Cyc VAT')
    locality = fields.Char('Locality')
    cyc_state = fields.Char('Cyc State')
    postal_code = fields.Char('Postal Code')
