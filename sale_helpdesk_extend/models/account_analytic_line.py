from odoo import models, fields



class AccountAnalyticLine(models.Model):
    """Inherited account.analytic.line for filter and groupby purpose"""

    _inherit = 'account.analytic.line'

    subtype_filter_id = fields.Many2one(related='helpdesk_ticket_id.subtype_id', store=True)
    ticket_filter_type_id = fields.Many2one(related='helpdesk_ticket_id.ticket_type_id',store=True)
