# -*- coding: utf-8 -*-
{
    'name': "boletax_contact_field_ext",

    'summary': """
        -Extensión de modelo res.partner """,

    'description': """
        - Incorporación de campo apikey
    """,

    'author': "Giraffos",
    'website': "http://www.giraffos.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base'
        ],
    'external_dependencies': {
        'python': [
            'boto3'
        ]
    },
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/cron.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
