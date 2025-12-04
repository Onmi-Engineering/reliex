{
    'name': 'RELIEX Frecuency leads',
    'version': '17.0.0.1',
    'summary': 'Frecuency leads flow',
    'description': 'Frecuency leads flow',
    'category': 'ONMI developments',
    'author': 'ONMI Engineering',
    'license': 'LGPL-3',
    'depends': ['crm', 'onmi_reliex_contacts', 'onmi_reliex_operations'],
    'data': [
        'data/ir_cron_frecuency_lead.xml',
        'security/ir_model_access.xml',
        'views/frecuency_lead_views.xml',
        'views/incident_views.xml',
        'views/crm_lead_views.xml',
        'views/work_order_clean_views.xml',
        'views/sale_order_views.xml',
        'wizards/quotation_selection_wizard_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
