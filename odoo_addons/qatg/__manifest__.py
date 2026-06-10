# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'QATG',
    'version': '0.1',
    'summary': 'Quản lý Bán hàng',
    'sequence': 1,
    'description':
        """
        
        """,
    'category': 'Other',
    'website': '',
    'depends': ['base', 'hr', 'sale'],
    'data':
    [
        "views/qatg_employee_view.xml",
        "views/qatg_product_view.xml",
        "views/qatg_product_specs_view.xml",
        "views/qatg_product_specs_value_view.xml",
        "views/qatg_sale_view.xml",

    ],
    'installable': True,
    'application': True
}
