# -*- coding: utf-8 -*-
# © 2018-Today Tundra Consulting & Advisory (http://tundra-consulting.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields,api,_


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_amount = fields.Float(string="Task Amount")
    sale_order_id = fields.Many2one('sale.order',string="Sale Order")