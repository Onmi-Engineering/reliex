# -*- coding: utf-8 -*-
{
    'name': "midla_reliex_module.",

    'summary': "Module with improvements to Operations.",

    'description': """
This module adds functionality to the Operations module
    """,

    'category': 'ONMI developments',
    'author': 'ONMI Engineering',

    'version': '0.1',

    'depends': ['base',
                'web',
                'onmi_reliex_operations',
                'onmi_reliex_reports',
                'sale',
                'sale_crm'],

    'data': [
        'security/ir.model.access.csv',
        # 'views/work_order_plant_view_enh01.xml',
        'views/worksheet_view_enh01.xml',
        # 'views/crm_saleorder_doc_enh01.xml',
        # 'views/crm_saleorder_view_enh01.xml',
        'views/res_partner_enh01.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'midla_reliex_module/static/src/css/work_order_styles.css',
        ],
    },

}