{
    'name': 'UMKM Kitchen Management',
    'version': '17.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Odoo module for managing kitchen orders in UMKM settings',
    'author': 'Adrian Sutansaty',
    'website': '',
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/order_sequence.xml', 

        'views/menus.xml', 
        'views/menu_category_views.xml',
        'views/menu_views.xml',
        'views/order_views.xml','views/dashboard_views.xml',
        
        'reports/report_order_details.xml',
        'reports/report_order_template.xml',
    ],
    'installable': True,
    'application': True,
}