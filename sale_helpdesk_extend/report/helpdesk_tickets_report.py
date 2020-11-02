# -*- coding: utf-8 -*-

from odoo import api, models
from datetime import datetime

class HelpdeskTicketReport(models.AbstractModel):
    """Class for report tickets."""

    _name = 'report.sale_helpdesk_extend.ticket_report_template'

    @api.model
    def get_report_values(self, docids, data=None):
        """Method call for get report data."""
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
        }
        
    