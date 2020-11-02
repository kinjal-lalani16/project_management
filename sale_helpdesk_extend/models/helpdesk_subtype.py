# -*- coding: utf-8 -*-
# © 2018-Today Tundra Consulting & Advisory (http://tundra-consulting.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class HelpdeskSubtype(models.Model):
    """Used for relate subtypes."""
    _name = "helpdesk.subtype"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(string="Name", translate=True,
                       track_visibility='onchange')
