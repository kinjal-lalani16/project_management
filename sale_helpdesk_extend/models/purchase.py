# -*- coding: utf-8 -*-
# © 2018-Today Tundra Consulting & Advisory (http://tundra-consulting.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _get_po_terms_conditions(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        if ICPSudo.get_param('sale_helpdesk_extend.use_purchase_note', False):
            return ICPSudo.get_param('sale_helpdesk_extend.purchase_note')
