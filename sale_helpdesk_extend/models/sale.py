# -*- coding: utf-8 -*-
# © 2018-Today Tundra Consulting (http://tundra-consulting.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models

class SaleOrderLine(models.Model):

	_inherit = 'sale.order.line'

	@api.onchange('product_uom')
	def product_uom_change(self):
		'''
		This method is used to stop default 
		functionality on change of quantity in sale quotation line.
		----------------------------------------------------
		@param self: object pointer
		'''
		return super(SaleOrderLine, self).product_uom_change()

	@api.onchange('product_id', 'price_unit', 'product_uom', 'tax_id')
	def _onchange_discount(self):
		'''
		This method is used to stop default 
		functionality on change of quantity in sale quotation line.
		----------------------------------------------------
		@param self: object pointer
		'''
		return super(SaleOrderLine, self)._onchange_discount()


	def _timesheet_find_project(self):
		'''
		This method is used to add project name as per our requirement 
		when project is created from sale order.
		'''
		# self.ensure_one()
		Project = self.env['project.project']
		project = self.product_id.with_context(force_company=self.company_id.id).project_id
		if not project:
			# find the project corresponding to the analytic account of the sales order
			account = self.order_id.analytic_account_id
			if not account:
				self.order_id._create_analytic_account(prefix=self.product_id.default_code or None)
				account = self.order_id.analytic_account_id
			project = Project.search([('analytic_account_id', '=', account.id)], limit=1)
			if not project:
				if self.product_id.service_tracking in ['task_new_project', 'project_only']:
					project_name = self.order_id.name + '-' + self.order_id.client_order_ref if self.order_id.client_order_ref else self.order_id.name 
				else:
					project_name = '%s (%s)' % (account.name, self.order_partner_id.ref) if self.order_partner_id.ref else account.name
				project = Project.create({
					'name': project_name,
					'allow_timesheets': self.product_id.service_type == 'timesheet',
					'analytic_account_id': account.id,
				})
				# set the SO line origin if product should create project
				if not project.sale_line_id and self.product_id.service_tracking in ['task_new_project', 'project_only']:
					project.write({'sale_line_id': self.id})
		return project