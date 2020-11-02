# -*- coding: utf-8 -*-
# © 2018-Today Aktiv Software (http://aktivsoftware.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class MrpProduction(models.Model):
	
	_inherit = "mrp.production"

	customer = fields.Char(string='Customer')

	@api.model
	def create(self, values):
		'''This method is used to add changes at the time of record creation.'''
		res = super(MrpProduction, self).create(values)
		if values.get('origin'):
			order_id = self.env['sale.order'].search([('name','=',values['origin'])])
			if order_id:
				res.customer = order_id.partner_id.name
		return res