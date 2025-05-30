{
    'name': 'RELIEX Automatic transfer between accounts.',
    'version': '17.0.0.1',
    'summary': 'Automatic transfer between accounts.',
    'description': 'Establishments and Plants on contacts.',
    'category':  'ONMI developments',
    'author': 'ONMI Engineering',
    'license': 'LGPL-3',
    'depends': ['account', 'resource'],
    'data': [
        'security/model_access.xml',
        'views/account_bank_statement_line_views.xml',
        'wizards/bank_to_cash_trans_wizard_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
