{
    'name': 'ONMI - RELIEX Custom calendar',
    'version': '17.0.0.1',
    'summary': 'ONMI Calendar customs',
    'description': 'Customizations to module Odoo Calendar.',
    'category':  'ONMI developments',
    'author': 'ONMI Engineering',
    'license': 'LGPL-3',
    'depends': ['calendar', 'web'],
    "assets": {
        "web.assets_backend": [
            "custom_calendar/static/src/css/custom_calendar.css",
        ]
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}