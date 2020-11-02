# -*- coding: utf-8 -*-
# © 2018-Today Tundra Consulting (http://tundra-consulting.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError , ValidationError


class HelpdeskTicket(models.Model):

    _inherit = 'helpdesk.ticket'

    partner_ids = fields.Many2many('res.partner', string='Contacts')
    contact_ids = fields.Many2one('res.partner', string='Main Contact')
    subtype_ids = fields.Selection([('1','Altres'),('2','Corrent / General'),('3','Corrent / Tempesta'),('4','Hardware / Altres'),('5','Hardware / Armari de Bateries'),('6','Hardware / Camera'),('7','Hardware / Comunicacions'),('8','Hardware / EC'),('9','Hardware / Gravadors'),('10','Hardware / IR'),('11','Hardware / Monitors'),('12','Hardware / NAS'),('13','Hardware / Optica'),('14','Hardware / Radar'),('15','Hardware / Server'),('16','Hardware / Switch'),('17','Hardware / Videowall'),('18','Satisfacció post venta'),('19','Software / Axis S.O.'),('20','Software / Helix'),('21','Software / onCamera'),('22','Software / S.O.'),('23','Software / SR7'),('24','Software / VaxALPR'),('25','Software Exacq'),('26','Vandalisme'),('27','Xarxa / Altres'),('28','Xarxa / Antenes')],string='Subtype Selection')
    total_time = fields.Float(string="Total Time Spent",
                              compute='compute_total_time')
    sales_agent_id = fields.Many2one(
        related='partner_id.user_id', string='Salesperson', store=True, readonly=True)
    subtype_id = fields.Many2one('helpdesk.subtype', string='Subtype')

    @api.multi
    @api.depends('timesheet_ids.unit_amount')
    def compute_total_time(self):
        '''This method is used to calculate total time.'''
        for ticket in self:
            total_time = 0
            if ticket.timesheet_ids:
                for timesheet in ticket.timesheet_ids:
                    total_time += timesheet.unit_amount
                ticket.total_time = total_time

    @api.onchange('partner_id', 'project_id')
    def _onchange_partner_project(self):
        # Added domain to Client Customer field to display selected Customer field value related contacts
        domain = [('parent_id','!=', False)]
        if self.partner_id:
            domain = [('parent_id','=', self.partner_id.id)]

        partner_ids = [rec.id for rec in self.partner_id.child_ids if rec.is_sat]
        self.partner_ids = [(6,0,partner_ids)]
        # Filer task based on stage sequence
        task_domain = self.set_task()
        return {'domain' : {'contact_ids' : domain, 'task_id': task_domain}}

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        '''This method is used to reset value of Contact field.'''
        res = self._onchange_partner_project()
        if self.partner_id and self.partner_id != self.contact_ids.parent_id:
            self.contact_ids = False
        return res

    # @api.onchange('contact_ids')
    # def _onchange_contact_ids(self):
    #     '''
    #     This method is used to get set partner based on selected contact
    #     onchange of contact in helpdesk ticket .
    #     ----------------------------------------------------
    #     @param self: object pointer
    #     '''
    #     domain = []
    #     if self.contact_ids and self.contact_ids.parent_id:
    #         self.partner_id =  self.contact_ids.parent_id.id
    #         domain = [('partner_id', '=', self.contact_ids.parent_id.id)]

    #     return {'domain': {'partner_id': domain }}


    def set_task(self):
        '''This method is used to set task as per sequence.'''
        domain = []
        if self.project_id :
            stage_ids = self.env['project.task.type'].search(
                [('project_ids','in',[self.project_id.id])],order="sequence ASC")
            domain = [('project_id','=',self.project_id.id), ('partner_id','=',self.partner_id.id)]
            task_ids = self.env['project.task'].search(domain, order="sequence ASC")
            task_id = False
            for stage in stage_ids:
                task_id = task_ids.filtered(lambda l: l.stage_id == stage)
                if task_id:
                    self.task_id = task_id[0]
                    break
        return domain

    @api.model
    def create(self, vals):
        '''
        This method is used to remove customer from follower list.
        ----------------------------------------------------
        @param self: object pointer
        '''
        res = super(HelpdeskTicket, self).create(vals)
        model_follower_obj = self.env['mail.followers']
        found_partner_follower = model_follower_obj.search(
                [('partner_id', '=', res.partner_id.id), ('res_model', '=', 'helpdesk.ticket'), ('res_id', '=', res.id)])

        # Remove partner/customer from follower list
        if found_partner_follower:
            found_partner_follower.unlink()
        return res

    @api.multi
    def write(self, vals):
        '''
        This method is used to add sales person as follower
        and will remove customer from follower list.
        ----------------------------------------------------
        @param self: object pointer
        '''
        model_follower_obj = self.env['mail.followers']
        # odoo automatically add partner in follower list so removed manually from
        # vals.
        if vals.get('message_follower_ids'):
            partner_id_list = [iter2.get('partner_id') for iter1 in vals.get(
                'message_follower_ids') for iter2 in iter1 if isinstance(iter2, dict)]
            if self.partner_id.id in partner_id_list:
                vals.pop('message_follower_ids')
        if self.sales_agent_id:
            found_follower = model_follower_obj.search(
                [('partner_id', '=', self.sales_agent_id.partner_id.id), ('res_model', '=', 'helpdesk.ticket'), ('res_id', '=', self.id)])
            found_partner_follower = model_follower_obj.search(
                [('partner_id', '=', self.partner_id.id), ('res_model', '=', 'helpdesk.ticket'), ('res_id', '=', self.id)])
            # Check if follower is not added in list it will add
            if not found_follower:
                model_follower_obj.create(
                    {'partner_id': self.sales_agent_id.partner_id.id, 'res_model': 'helpdesk.ticket', 'res_id': self.id})
            # Remove partner/customer from follower list
            if found_partner_follower:
                found_partner_follower.unlink()
        res = super(HelpdeskTicket, self).write(vals)
        return res

    def send_mail_contacts(self):
        '''
        This method is used to send and email to all
        contacts and followers of helpdesk ticket.
        ----------------------------------------------------
        @param self: object pointer
        '''
        self.ensure_one()
        # Search for Solved stage and update in Helpdesk ticket
        stage = self.env['helpdesk.stage'].search([('is_solved','=', True)], limit=1)
        if not stage:
            raise UserError(_('Please activate Solved feature from Helpdesk Stage.'))
        self.write({'stage_id': stage.id})

        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference(
                'sale_helpdesk_extend', 'helpdesk_mail_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        #Set default recipients to compose box which are contacts + followers.
        partners = []
        for partner in self.partner_ids:
                partners.append(partner.id)
        for followers in self.message_follower_ids:
                partners.append(followers.partner_id.id)
        partners = list(set(partners))

        ctx = {
            'default_model': 'helpdesk.ticket',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
            'default_partner_ids': partners,
            'custom_layout': "sale.mail_template_data_notification_email_sale_order",
            'default_stage': True,
        }

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def notify_mail_contacts(self):
        '''
        This method is used to send and email to all
        contacts and followers of helpdesk ticket.
        ----------------------------------------------------
        @param self: object pointer
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference(
                'sale_helpdesk_extend', 'helpdesk_mail_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        #Set default recipients to compose box which are contacts + followers.
        partners = []
        for partner in self.partner_ids:
                partners.append(partner.id)
        for followers in self.message_follower_ids:
                partners.append(followers.partner_id.id)
        partners = list(set(partners))

        ctx = {
            'default_model': 'helpdesk.ticket',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
            'default_partner_ids': partners,
            'custom_layout': "sale.mail_template_data_notification_email_sale_order",
            'default_stage': True,
        }

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

