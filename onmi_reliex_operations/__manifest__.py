{
    'name': 'RELIEX Operations.',
    'version': '17.0.0.1',
    'summary': 'New main menu Operations.',
    'description': 'New main menu Operations.',
    'category': 'ONMI developments',
    'author': 'ONMI Engineering.',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'product', 'onmi_reliex_contacts', 'sale', 'sale_crm', 'purchase', 'hr', 'mail'],
    'data': [
        'data/work_order_clean_data.xml',
        'data/ir_action_server_data.xml',
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
        'data/documents_data.xml',
        'security/model_access.xml',
        # 'views/calendar_style.xml',
        'views/sign_info_wizard_views.xml',
        'views/menuitem.xml',
        'views/work_order_clean_views.xml',
        'views/work_order_plant_views.xml',
        'views/material_list_views.xml',
        'views/incident_views.xml',
        'views/worksheet_views.xml',
        'views/purchase_order_views.xml',
        'views/checklist_views.xml',
        'views/checklist_fire_views.xml',
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'onmi_reliex_operations/static/src/css/calendar_style.css',
    #     ],
    # },
    'installable': True,
    'application': True,
    'auto_install': False
}
