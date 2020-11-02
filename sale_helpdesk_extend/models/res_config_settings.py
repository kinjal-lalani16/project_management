# -*- coding: utf-8 -*-
# © 2018-Today Tundra Consulting & Advisory (http://tundra-consulting.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    purchase_note = fields.Text(string="Terms & Conditions")
    use_purchase_note = fields.Boolean(
        string='Default Terms & Conditions',)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            use_purchase_note=ICPSudo.get_param(
                'sale_helpdesk_extend.use_purchase_note', default=False),
            purchase_note=ICPSudo.get_param(
                'sale_helpdesk_extend.purchase_note'),
        )
        return res

    @api.multi
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param(
            "sale_helpdesk_extend.use_purchase_note", self.use_purchase_note)
        ICPSudo.set_param(
            "sale_helpdesk_extend.purchase_note", self.purchase_note)
        return res
