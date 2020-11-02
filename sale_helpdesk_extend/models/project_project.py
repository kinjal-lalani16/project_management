# -*- coding: utf-8 -*-
# © 2018-Today Tundra Consulting & Advisory (http://tundra-consulting.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = 'project.project'
    stage = fields.Selection([
        ('1_new', 'New'),
        ('2_sat', 'SAT'),
        ('3_planned', 'Planned'),
        ('4_executed', 'Executed'),
        ('5_quality_control', 'Quality Control'),
        ('6_delivery_training', 'Deliver-Training'),
        ('7_on_hold', 'On hold'),
    ], string="Stage", default='1_new')
    end_date = fields.Date(string='End date')
    number_of_days = fields.Integer(
        string='Number of Days', compute='calculate_number_of_day', store=True)

    @api.depends('create_date', 'end_date')
    def calculate_number_of_day(self):
        """ This method will giv difference between create_date and
        end_date..!"""
        for rec in self:
            if rec.create_date and rec.end_date:
                create_date = datetime.strptime(
                    rec.create_date, "%Y-%m-%d %H:%M:%S").date()
                end_date = datetime.strptime(rec.end_date, "%Y-%m-%d").date()
                rec.number_of_days = (end_date - create_date).days

    @api.constrains('create_date', 'end_date')
    def check_date(self):
        if self.create_date and self.end_date and self.create_date > self.end_date:
            raise ValidationError("End date cannot be less then start date")
        return True
