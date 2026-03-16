{
    'name' : "Equipment Maintenance ERP",
    'version': "18.0.1.0.1",
    'license': "LGPL-3",
    'summary': """Custom Odoo module for managing equipment maintenance""",
    'description': """
                    Test task for Odoo developer (3-day deadline).

                    The "Equipment Maintenance" module allows you to:
                    - track and manage equipment,
                    - create and process maintenance requests,
                    - monitor execution status,
                    - store maintenance history,
                    - generate analytics via Pivot tables and reports,
                    - restrict access through the portal.
                    """,
    'author': "Bohdan Ghoul",
    'category': "Test Task for Odoo developer",
    # 'website': "",
    'maintainer': "Bohdan Ghoul",
    'sequence': 1,
    'depends': [
        'base',
        'portal',
        'website',
    ],
    'assets': {
    'web.assets_backend': [
            'equipment_maintenance_erp/static/src/components/**/*.js',
            'equipment_maintenance_erp/static/src/components/**/*.xml',
        ],
    },
    'data': [
        "security/equipment_maintenance_erp_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/equipment_category_views.xml",
        "views/equipment_views.xml",
        "views/maintenance_request_views.xml",
        "views/history_views.xml",
        "views/report_views.xml",
        "views/portal_details.xml",
        "views/portal_home.xml",
        "views/portal_create_requests.xml",
        "views/dashboard_views.xml",
        "views/equipment_maintenance_erp_menu.xml",
    ],
    'application': True,
    'auto_install': False,
    'installable': True,
}

