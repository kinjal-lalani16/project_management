# -*- coding: utf-8 -*-
# © 2018-Today Tundra Consulting & Advisory (http://tundra-consulting.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields,api,_

class ProjectProject(models.Model):

	_inherit = 'project.project'

	stage = fields.Selection([
		('1_new','New'),
		('2_sat','SAT'),
		('3_planned','Planned'),
		('4_executed','Executed'),
		('5_quality_control','Quality Control'),
		('6_delivery_training','Deliver-Training'),
		('7_on_hold','On hold'),
		],string="Stage",default='1_new')