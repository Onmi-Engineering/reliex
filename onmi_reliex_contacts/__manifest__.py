{
    'name': 'RELIEX Contacts',
    'version': '17.0.0.1',
    'summary': 'Establishments and Plants on contacts.',
    'description': 'Establishments and Plants on contacts.',
    'category':  'ONMI developments',
    'author': 'ONMI Engineering',
    'license': 'LGPL-3',
    'depends': ['base', 'crm', 'sale_crm'],
    'data': [
        'data/crm_stage_data.xml',
        'security/model_access.xml',
        'views/sale_order_views.xml',
        'views/res_partner_views.xml',
        'views/crm_stage_views.xml',
        'views/crm_lead_views.xml',
        'views/product_template_views.xml',
        'views/cyc_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
