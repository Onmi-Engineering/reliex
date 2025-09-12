{
    'name': 'RELIEX Commercial',
    'version': '17.0.0.1',
    'summary': 'Commercial issues',
    'description': 'Commercial issues',
    'category': 'ONMI developments',
    'author': 'ONMI Engineering',
    'license': 'LGPL-3',
    'depends': ['contacts', 'onmi_reliex_operations', 'onmi_reliex_contacts'],
    'data': [
        'data/ir_cron_data.xml',
        'report/ir_model_access.xml',
        'views/res_partner_views.xml',
        'views/duct_register_views.xml',
        'views/sale_order_views.xml',
        'views/crm_lead_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
