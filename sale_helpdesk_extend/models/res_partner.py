# -*- coding: utf-8 -*-
# © 2018-Today Tundra Consulting & Advisory (http://tundra-consulting.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields,api,_, tools


class PoliceType(models.Model):

    _name = 'police.type'
    _description = 'Police Type'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=1)

class ResRegion(models.Model):

    _name = 'res.region'
    _description = 'Region'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=1)

class ResPartner(models.Model):
    
    _inherit = 'res.partner'

    is_sat = fields.Boolean(string="Is Sat")
    disable_customer = fields.Boolean(string="Disabled")
    average_time = fields.Float(string="Average Time",compute='compute_average_total_time')
    total_time = fields.Float(string="Total Spent Time",compute='compute_average_total_time')
    alph_customer = fields.Boolean(string="Alphanet Customer")
    alph_customer_date = fields.Date(string="Customer since")
    satisfaction = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10')])
    useit = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10')])
    policetype_id = fields.Many2one('police.type', string='Police Type')
    is_invoicing = fields.Boolean(string="Invoicing")
    region_id = fields.Many2one('res.region', string='Region')

    @api.multi
    @api.depends('ticket_count')
    def compute_average_total_time(self):
        '''This method is calculate average time.'''
        for partner in self:
            total_time = 0
            partner_tickets = self.env['helpdesk.ticket'].sudo().search([('partner_id', '=', partner.id)])
            if partner_tickets:
                for ticket in partner_tickets:
                   total_time += ticket.total_time
                partner.total_time = total_time
                partner.average_time = total_time/len(partner_tickets)

    @api.model
    def create(self, vals):
        if vals.get('parent_id', False):
            vals.update({
                'policetype_id': self.browse(vals['parent_id']).policetype_id.id
            })
        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('parent_id', False):
            vals.update({
                'policetype_id': self.browse(
                    vals['parent_id']).policetype_id.id
            })
        elif vals.get('policetype_id', False) and self.company_type == 'company' and self.child_ids:
            for child in self.child_ids:
                child.write({
                    'policetype_id': vals['policetype_id']
                })
        return super(ResPartner, self).write(vals)