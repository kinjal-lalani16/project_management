# -*- coding: utf-8 -*-
# © 2018-Today Tundra Consulting (http://tundra-consulting.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Sale Helpdesk Extend",
    'version': "11.0.1.6.3",
    'summary': """Mail fuctionality in helpdesk ticket is added and in
    sale order quoation line price and discount will not be updated
    while changing quantity.""",
    'description':
    """
    Using this module in helpdesk if we select the customer it will
    display the records in list who belongs to that customer and Is Sat
    field is set to true.A new field is added in helpdesk ticket stage
    if it is true then only mail functionality will run.A button is added
    in Helpdesk ticket form and on click of that wizard for mail will be
    opened and clicking send button mail will be sent.In Sales Quotation
    Line after setting product price if we update quantity it will not
    change updated price and discount in quotation line. Functionality
    of updating price and discount on change of quantity has been stopped.

    Module can also count "Average Time" of each and every helpdesk tickets.
    """,
    'author': "Tundra Consulting & Advisory SL",
    'company': "Tundra Consulting & Advisory SL",
    'website': "www.tundra-consulting.com",
    'category': "Sales",
    'depends': ['sale', 'sale_management', 'helpdesk','mrp','helpdesk_timesheet','base','project','contacts','sale_timesheet', 'purchase'],
    'data': [
        'data/helpdesk_email_template.xml',
        'security/ir.model.access.csv',
        'views/helpdesk_stage.xml',
        'views/account_analytic_line.xml',
        'views/res_partner_view.xml',
        'views/helpdesk_view.xml',
        'views/mrp_production_view.xml',
        'views/project_task_amount_view.xml',
        'views/project_task_inherit_view.xml',
        'views/police_type_view.xml',
        'views/res_region_view.xml',
        'views/project_project_view.xml',
        'views/res_config_settings_views.xml',
        'views/helpdesk_subtype_views.xml',
        'report/sale_report_template.xml',
        'report/report_helpdesk_tickets_template.xml',
        'report/report_helpdesk_tickets.xml',
        'report/report_purchase_order.xml',
        'wizard/helpdesk_ticket_report_view.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}