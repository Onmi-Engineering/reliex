{
    'name': 'RELIEX Fleet.',
    'version': '17.0.0.1',
    'summary': 'ONMI Fleet customs.',
    'description': 'Customizations to module Odoo Fleet.',
    'category':  'ONMI developments',
    'author': 'ONMI Engineering',
    'license': 'LGPL-3',
    'depends': ['fleet', 'mail'],
    'data': [
        'data/mail_template_data.xml',
        'views/fleet_vehicle_log_services_views.xml',
        'views/fleet_vehicle_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
