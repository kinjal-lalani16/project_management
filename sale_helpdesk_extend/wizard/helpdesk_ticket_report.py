# -*- coding: utf-8 -*-
# © 2018-Today Aktiv Software (http://aktivsoftware.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError, UserError
import base64
import io
import xlsxwriter

subtype_values = [('1', 'Altres'), ('2', 'Corrent / General'), ('3', 'Corrent / Tempesta'), ('4', 'Hardware / Altres'), ('5', 'Hardware / Armari de Bateries'), ('6', 'Hardware / Camera'), ('7', 'Hardware / Comunicacions'), ('8', 'Hardware / EC'), ('9', 'Hardware / Gravadors'), ('10', 'Hardware / IR'), ('11', 'Hardware / Monitors'), ('12', 'Hardware / NAS'), ('13', 'Hardware / Optica'), ('14', 'Hardware / Radar'),
                  ('15', 'Hardware / Server'), ('16', 'Hardware / Switch'), ('17', 'Hardware / Videowall'), ('18', 'Satisfacció post venta'), ('19', 'Software / Axis S.O.'), ('20', 'Software / Helix'), ('21', 'Software / onCamera'), ('22', 'Software / S.O.'), ('23', 'Software / SR7'), ('24', 'Software / VaxALPR'), ('25', 'Software Exacq'), ('26', 'Vandalisme'), ('27', 'Xarxa / Altres'), ('28', 'Xarxa / Antenes')]


class HelpdeskTicketReport(models.TransientModel):

    _name = "helpdesk.ticket.report"

    partner_ids = fields.Many2many('res.partner', string="Customer Name")
    start_date = fields.Date(string='From Date', required=True)
    end_date = fields.Date(string='To Date', required=True)
    report_type = fields.Selection([('internal', 'Internal'), ('external', 'External')])

    @api.multi
    @api.constrains('start_date', 'end_date')
    def check_date(self):
        """ This method is used to check constrains on dates."""
        if self.start_date and self.end_date and (self.start_date > self.end_date):
            raise ValidationError(
                _('End date should be greater than start date.'))

    @api.multi
    def get_period_ticket(self, ticket_type):
        # Get ticket count for selected period 
        ticket_domain = [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date)]
        if self.partner_ids:
            ticket_domain += [('partner_id', 'in', self.partner_ids.ids)]
        # Add domin for closed ticket
        if ticket_type == 'closed':
            stages = self.env['helpdesk.stage'].search([('is_solved', '=', True), ('name', '!=', 'Cancelled')])
            ticket_domain.append(('stage_id', 'in', stages.ids))
        # Add domin for closed ticket
        if ticket_type == 'open':
            stages = self.env['helpdesk.stage'].search([('is_solved', '!=', True), ('name', '!=', 'Cancelled')])
            ticket_domain.append(('stage_id', 'in', stages.ids))
        # Search ticket based on applied filter
        ticket_ids = self.env['helpdesk.ticket'].search_count(ticket_domain)
        return ticket_ids

    @api.multi
    def get_open_ticket(self):
        stages = self.env['helpdesk.stage'].search(
            [('is_solved', '!=', True), ('name', '!=', 'Cancelled')])
        domain = [('stage_id', 'in', stages.ids)]
        if self.partner_ids:
            domain += [('partner_id', 'in', self.partner_ids.ids)]
        ticket_ids = self.env['helpdesk.ticket'].search_count(domain)
        return ticket_ids

    @api.multi
    def get_stage(self):
        stages = self.env['helpdesk.stage'].search([])
        return stages

    @api.multi
    def get_ticket_type(self):
        domain = self.get_date_domain()
        domain.append(('ticket_type_id', '!=', False))
        if self.partner_ids:
            domain += [('partner_id', 'in', self.partner_ids.ids)]
        ticket_ids = self.env['helpdesk.ticket'].search(domain)
        ticket_type = [ticket.ticket_type_id for ticket in ticket_ids]
        return list(set(ticket_type))

    @api.multi
    def get_subtypes(self):
        domain = self.get_date_domain()
        if self.partner_ids:
            domain += [('partner_id', 'in', self.partner_ids.ids)]
        domain.append(('subtype_ids', '!=', False))
        ticket_ids = self.env['helpdesk.ticket'].search(domain)
        subtypes = [ticket.subtype_id for ticket in ticket_ids if ticket.subtype_id]
        return set(subtypes)

    @api.multi
    def get_ticket_stage_count(self, stage):
        domain = self.get_date_domain()
        domain += [('stage_id', '=', stage.id)]
        if self.partner_ids:
            domain += [('partner_id', 'in', self.partner_ids.ids)]
        ticket_count = self.env['helpdesk.ticket'].search_count(domain)
        return ticket_count

    @api.multi
    def get_ticket_ticket_type_count(self, ticket_type):
        domain = self.get_date_domain()
        domain.append(('ticket_type_id', '=', ticket_type.id))
        if self.partner_ids:
            domain += [('partner_id', 'in', self.partner_ids.ids)]
        ticket_count = self.env['helpdesk.ticket'].search_count(domain)
        return ticket_count

    @api.multi
    def get_ticket_sum_hours_dedicate(self, ticket_type):
        domain = self.get_date_domain()
        domain.append(('ticket_type_id', '=', ticket_type.id))
        if self.partner_ids:
            domain += [('partner_id', 'in', self.partner_ids.ids)]
        ticket_ids = self.env['helpdesk.ticket'].search(domain)

        total_hours = 0.0
        for ticket in ticket_ids:
            total_hours += ticket.total_time

        return total_hours

    @api.multi
    def get_ticket_sum_hours_dedicate_per(self, ticket_type):
        domain = self.get_date_domain()
        domain.append(('ticket_type_id', '!=', False))
        if self.partner_ids:
            domain += [('partner_id', 'in', self.partner_ids.ids)]
        all_ticket_ids = self.env['helpdesk.ticket'].search(domain)

        all_total_hours = 0.0
        for ticket in all_ticket_ids:
            all_total_hours += ticket.total_time
        total_hours = self.get_ticket_sum_hours_dedicate(ticket_type)
        try:
            per_total_hours = (total_hours * 100) / all_total_hours
        except ZeroDivisionError:
            per_total_hours = 0.0

        return per_total_hours

    @api.multi
    def get_ticket_avg_day(self, ticket_type):
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
        date_diff = end_date - start_date
        ticket_count = self.get_ticket_ticket_type_count(ticket_type)
        try:
            avg_ticket = ticket_count / date_diff.days
        except ZeroDivisionError:
            avg_ticket = 0.0
        return avg_ticket

    @api.multi
    def get_ticket_avg_hours(self, ticket_type):
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
        date_diff = end_date - start_date
        ticket_hours = self.get_ticket_sum_hours_dedicate(ticket_type)
        avg_ticket_hours = 0.0
        try:
            avg_ticket_hours = ticket_hours / date_diff.days
        except ZeroDivisionError:
            avg_ticket_hours = 0.0
        return avg_ticket_hours

# Subtypes

    @api.multi
    def get_subtype_count(self, subtype):
        domain = self.get_date_domain()
        domain.append(('subtype_ids', '=', subtype))
        if self.partner_ids:
            domain += [('partner_id', 'in', self.partner_ids.ids)]
        ticket_count = self.env['helpdesk.ticket'].search_count(domain)
        return ticket_count

    @api.multi
    def get_subtype_sum_hours_dedicate(self, subtype):
        domain = self.get_date_domain()
        domain.append(('subtype_ids', '=', subtype))
        if self.partner_ids:
            domain += [('partner_id', 'in', self.partner_ids.ids)]
        ticket_ids = self.env['helpdesk.ticket'].search(domain)

        total_hours = 0.0
        for ticket in ticket_ids:
            total_hours += ticket.total_time

        return total_hours

    @api.multi
    def get_subtype_sum_hours_dedicate_per(self, subtype):
        domain = self.get_date_domain()
        domain.append(('subtype_ids', '!=', False))
        if self.partner_ids:
            domain += [('partner_id', 'in', self.partner_ids.ids)]
        all_ticket_ids = self.env['helpdesk.ticket'].search(domain)

        all_total_hours = 0.0
        for ticket in all_ticket_ids:
            all_total_hours += ticket.total_time
        total_hours = self.get_subtype_sum_hours_dedicate(subtype)
        try:
            per_total_hours = (total_hours * 100) / all_total_hours
        except ZeroDivisionError:
            per_total_hours = 0.0

        return per_total_hours

    @api.multi
    def get_subtype_avg_day(self, subtype):
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
        date_diff = end_date - start_date
        ticket_count = self.get_subtype_count(subtype)
        avg_ticket = 0
        days = date_diff.days
        try:
            if days == 0:
                days = 1
            avg_ticket = ticket_count / days
        except ZeroDivisionError:
            avg_ticket = 0.0
        return avg_ticket

    @api.multi
    def get_subtype_avg_hours(self, subtype):
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
        date_diff = end_date - start_date
        ticket_hours = self.get_subtype_sum_hours_dedicate(subtype)
        avg_ticket_hours = 0.0
        days = date_diff.days
        try:
            if days == 0:
                days = 1
            avg_ticket_hours = ticket_hours / days
        except ZeroDivisionError:
            avg_ticket_hours = 0.0
        return avg_ticket_hours

    @api.multi
    def get_date_domain(self):
        domain = [
            ('create_date', '>=', self.start_date),
            ('create_date', '<=', self.end_date)]
        return domain

    @api.multi
    def get_partners(self):
        partner_obj = self.env['res.partner']
        domain = self.get_date_domain()
        if self.partner_ids:
            domain += [('partner_id', 'in', self.partner_ids.ids)]
        ticket_ids = self.env['helpdesk.ticket'].search(domain)
        partner_ids = list(
            set([ticket.partner_id.id for ticket in ticket_ids]))
        partner_recs = partner_obj.browse(partner_ids)
        return partner_recs

    @api.multi
    def get_tickets(self, partner):
        domain = self.get_date_domain()
        if partner:
            domain.append(('partner_id', '=', partner.id))
        ticket_ids = self.env['helpdesk.ticket'].search(domain)
        return ticket_ids

    @api.multi
    def sum_calculate_total_time(self, ticket_ids):
        total_time1 = 0
        for ticket in ticket_ids:
            total_time1 += ticket.total_time
        return total_time1

    @api.multi
    def calculate_total_time(self, partner):
        ticket_recs = self.get_tickets(partner)
        total_time = self.sum_calculate_total_time(ticket_recs)
        return total_time

    @api.multi
    def calculate_average_time(self, partner):
        ticket_recs = self.get_tickets(partner)
        total_time = self.calculate_total_time(partner)
        average_time = format(total_time / len(ticket_recs), '.2f')
        return average_time

    @api.multi
    def print_pdf(self):
        """Method call for check print report."""
        data = {}
        data['form'] = self.read(['partner_ids', 'start_date', 'end_date'])[0]
        ticket_recs = self.get_partners()
        if not ticket_recs:
            raise UserError(
                _('No ticket found.'))
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(
            self.read(['partner_ids', 'start_date', 'end_date'])[0])
        return self.env.ref('sale_helpdesk_extend.ticket_report_view').report_action(
            self, data=data, config=False)

    @api.multi
    def print_xls(self):
        ticket_recs = self.get_partners()
        if not ticket_recs:
            raise UserError(
                _('No ticket found.'))
        fp = io.BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet('Report')
        data_format = workbook.add_format({'align': 'center'})
        report_header_format = workbook.add_format(
            {'bold': True, 'align': 'center', 'font_size': 18})
        header_format = workbook.add_format({'bold': True, 'align': 'center'})
        bold = workbook.add_format({'bold': True})
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
        not_exist = workbook.add_format({'bold': True, 'font_color': 'red'})
        row = 0
        colm = 0
        header_string = 'Helpdesk Ticket Report From ' + \
            str(self.start_date) + ' to ' + str(self.end_date)
        worksheet.merge_range(
            'A1:H2', header_string, report_header_format)

        if self.partner_ids:
            row += 1
            partner_name = [partner.name for partner in self.get_partners()]
            worksheet.merge_range(
                'A3:H4', '(' + ','.join(partner_name) + ')', report_header_format)
        row += 3
        if not self.report_type or self.report_type == 'internal':
            worksheet.write(row, 0, 'Description', header_format)
            worksheet.write(row, 1, 'Ticket Count', header_format)

            row += 1
            ticket_count = self.get_period_ticket('created')
            worksheet.write(row, 0, 'Created', data_format)
            worksheet.write(row, 1, ticket_count, data_format)

            row += 1
            ticket_count = self.get_period_ticket('closed')
            worksheet.write(row, 0, 'Closed', data_format)
            worksheet.write(row, 1, ticket_count, data_format)

            row += 1
            ticket_count = self.get_period_ticket('open')
            worksheet.write(row, 0, 'Open', data_format)
            worksheet.write(row, 1, ticket_count, data_format)

            row += 1
            worksheet.write(row, 0, 'Total Open', data_format)
            open_ticket_count = self.get_open_ticket()
            worksheet.write(row, 1, open_ticket_count, data_format)

            row += 3
            worksheet.write(row, 0, 'Stage Name', header_format)
            worksheet.write(row, 1, 'Ticket Count', header_format)
            stages = self.get_stage()
            for stage in stages:
                row += 1
                ticket_count = self.get_ticket_stage_count(stage)
                worksheet.write(row, 0, stage.name, data_format)
                worksheet.write(row, 1, ticket_count, data_format)
            row += 1
            worksheet.write(row, 0, 'Total Open', data_format)
            open_ticket_count = self.get_open_ticket()
            worksheet.write(row, 1, open_ticket_count, data_format)

            row += 2

        worksheet.write(row, colm, 'Ticket type', header_format)
        colm += 1
        worksheet.write(row, colm, 'No of Tickets', header_format)
        colm += 1
        worksheet.write(row, colm, 'Sum hours dedicated', header_format)
        colm += 1
        worksheet.write(row, colm, '% Hours (to total)', header_format)
        if not self.report_type or self.report_type == 'internal':
            colm += 1
            worksheet.write(row, colm, 'Avg ticket/day', header_format)
            colm += 1
            worksheet.write(row, colm, 'Avg hours/day', header_format)

        total_ticket_type_count = 0
        total_ticket_sum_hours = 0
        total_ticket_sum_hours_dedicate_per = 0
        total_ticket_avg_day = 0
        total_ticket_avg_hours = 0

        ticket_types = self.get_ticket_type()
        for ticket in ticket_types:
            row += 1
            colm = 0
            no_of_tickets = self.get_ticket_ticket_type_count(ticket)
            sum_hours_dedicated = self.get_ticket_sum_hours_dedicate(ticket)
            hours_sum_percentage = self.get_ticket_sum_hours_dedicate_per(
                ticket)
            avg_ticket_per_day = self.get_ticket_avg_day(ticket)
            avg_hours_per_date = self.get_ticket_avg_hours(ticket)

            total_ticket_type_count += no_of_tickets
            total_ticket_sum_hours += sum_hours_dedicated
            total_ticket_sum_hours_dedicate_per += hours_sum_percentage
            total_ticket_avg_day += avg_ticket_per_day
            total_ticket_avg_hours += avg_hours_per_date
            worksheet.write(row, colm, ticket.name, data_format)
            colm += 1
            worksheet.write(row, colm, no_of_tickets, data_format)
            colm += 1
            sum_hours_dedicated = '%02d:%02d' % (
                int(float(sum_hours_dedicated)), float(sum_hours_dedicated) % 1 * 60)
            worksheet.write(row, colm, sum_hours_dedicated, data_format)
            colm += 1
            worksheet.write(row, colm, str(
                round(hours_sum_percentage, 2)) + ' %', data_format)
            if not self.report_type or self.report_type == 'internal':
                colm += 1
                worksheet.write(row, colm, round(
                    avg_ticket_per_day, 2), data_format)
                colm += 1
                avg_hours_per_date = '%02d:%02d' % (
                    int(float(avg_hours_per_date)), float(avg_hours_per_date) % 1 * 60)
                worksheet.write(row, colm, avg_hours_per_date, data_format)
        row += 1
        colm = 0
        worksheet.write(row, colm, 'Totals:', header_format)
        colm += 1
        worksheet.write(row, colm, total_ticket_type_count, data_format)
        colm += 1
        total_ticket_sum_hours = '%02d:%02d' % (
            int(float(total_ticket_sum_hours)), float(total_ticket_sum_hours) % 1 * 60)
        worksheet.write(row, colm, total_ticket_sum_hours, data_format)
        colm += 1
        worksheet.write(row, colm, str(
            round(total_ticket_sum_hours_dedicate_per, 2)) + ' %', data_format)
        if not self.report_type or self.report_type == 'internal':
            colm += 1
            worksheet.write(row, colm, round(total_ticket_avg_day, 2), data_format)
            colm += 1
            total_ticket_avg_hours = '%02d:%02d' % (
                int(float(total_ticket_avg_hours)), float(total_ticket_avg_hours) % 1 * 60)
            worksheet.write(row, colm, total_ticket_avg_hours, data_format)

        row += 2
        colm = 0

        worksheet.write(row, colm, 'Subtypes', header_format)
        colm += 1
        worksheet.write(row, colm, 'No of Tickets', header_format)
        colm += 1
        worksheet.write(row, colm, 'Sum hours dedicated', header_format)
        colm += 1
        worksheet.write(row, colm, '% Hours (to total)', header_format)
        if not self.report_type or self.report_type == 'internal':
            colm += 1
            worksheet.write(row, colm, 'Avg ticket/day', header_format)
            colm += 1
            worksheet.write(row, colm, 'Avg hours/day', header_format)

        subtypes_tickets = self.get_subtypes()
        total_subtype_type_count = 0
        total_subtype_sum_hours = 0
        total_subtype_sum_hours_dedicate_per = 0
        total_subtype_avg_day = 0
        total_subtype_avg_hours = 0
        for ticket in subtypes_tickets:
            row += 1
            colm = 0
            no_of_tickets = self.get_subtype_count(ticket.id)
            sum_hours_dedicated = self.get_subtype_sum_hours_dedicate(ticket.id)
            hours_sum_percentage = self.get_subtype_sum_hours_dedicate_per(ticket.id)
            avg_ticket_per_day = self.get_subtype_avg_day(ticket.id)
            avg_hours_per_date = self.get_subtype_avg_hours(ticket.id)

            total_subtype_type_count += no_of_tickets
            total_subtype_sum_hours += sum_hours_dedicated
            total_subtype_sum_hours_dedicate_per += hours_sum_percentage
            total_subtype_avg_day += avg_ticket_per_day
            total_subtype_avg_hours += avg_hours_per_date
            worksheet.write(row, colm, ticket.name, data_format)
            colm += 1
            worksheet.write(row, colm, no_of_tickets, data_format)
            colm += 1
            sum_hours_dedicated = '%02d:%02d' % (
                int(float(sum_hours_dedicated)), float(sum_hours_dedicated) % 1 * 60)
            worksheet.write(row, colm, sum_hours_dedicated, data_format)
            colm += 1
            worksheet.write(row, colm, str(
                round(hours_sum_percentage, 2)) + ' %', data_format)
            if not self.report_type or self.report_type == 'internal':
                colm += 1
                worksheet.write(row, colm, round(
                    avg_ticket_per_day, 2), data_format)
                colm += 1
                avg_hours_per_date = '%02d:%02d' % (
                    int(float(avg_hours_per_date)), float(avg_hours_per_date) % 1 * 60)
                worksheet.write(row, colm, avg_hours_per_date, data_format)
        row += 1
        colm = 0
        worksheet.write(row, colm, 'Totals:', header_format)
        colm += 1
        worksheet.write(row, colm, total_subtype_type_count, data_format)
        colm += 1
        total_subtype_sum_hours = '%02d:%02d' % (
            int(float(total_subtype_sum_hours)), float(total_subtype_sum_hours) % 1 * 60)
        worksheet.write(row, colm, total_subtype_sum_hours, data_format)
        colm += 1
        worksheet.write(row, colm, str(
            round(total_subtype_sum_hours_dedicate_per, 2)) + ' %', data_format)
        if not self.report_type or self.report_type == 'internal':
            colm += 1
            worksheet.write(row, colm, round(
                total_subtype_avg_day, 2), data_format)
            colm += 1
            total_subtype_avg_hours = '%02d:%02d' % (
                int(float(total_subtype_avg_hours)), float(total_subtype_avg_hours) % 1 * 60)
            worksheet.write(row, colm, total_subtype_avg_hours, data_format)

        row += 2
        colm = 0
        # if self.partner_ids:
        partner_recs = self.get_partners()
        for partner in partner_recs:
            row += 2
            worksheet.write(row, colm, 'Customer Name', header_format)
            colm += 1
            worksheet.write(row, colm, 'Total Time', header_format)
            colm += 1
            worksheet.write(row, colm, 'Average Time', header_format)

            row += 1
            colm = 0
            worksheet.write(row, colm, partner.name, data_format)

            colm += 1
            get_total_time = self.calculate_total_time(partner)
            total_total_time = '%02d:%02d' % (
                int(get_total_time), get_total_time % 1 * 60)
            worksheet.write(row, colm, total_total_time, data_format)

            colm += 1
            get_average_time = self.calculate_average_time(partner)
            total_average_time = '%02d:%02d' % (
                int(float(get_average_time)), float(get_average_time) % 1 * 60)
            worksheet.write(row, colm, total_average_time, data_format)

            tickets = self.get_tickets(partner)
            row += 3
            colm = 0
            if tickets:
                worksheet.write(row, colm, 'Ticket', header_format)
                colm += 1
                worksheet.write(row, colm, 'Customer Name', header_format)
                colm += 1
                worksheet.write(row, colm, 'Assigned to', header_format)
                colm += 1
                worksheet.write(row, colm, 'Helpdesk Team', header_format)
                colm += 1
                worksheet.write(row, colm, 'Ticket Type', header_format)
                colm += 1
                worksheet.write(row, colm, 'Created On', header_format)
                colm += 1
                worksheet.write(row, colm, 'Close Date', header_format)
                colm += 1
                worksheet.write(
                    row, colm, 'Total Spent Time', header_format)
                colm += 1
                row += 1
                for ticket in tickets:
                    colm = 0
                    row += 1
                    worksheet.write(
                        row, colm, ticket.name, data_format)
                    colm += 1
                    worksheet.write(
                        row, colm, ticket.partner_id.name, data_format)
                    colm += 1
                    worksheet.write(
                        row, colm, ticket.user_id.name, data_format)
                    colm += 1
                    worksheet.write(
                        row, colm, ticket.team_id.name, data_format)
                    colm += 1
                    worksheet.write(
                        row, colm, ticket.ticket_type_id.name, data_format)
                    colm += 1
                    date = datetime.strptime(
                        ticket.create_date, "%Y-%m-%d %H:%M:%S")
                    create_date = datetime.strftime(date, '%d-%m-%Y')
                    worksheet.write(
                        row, colm, create_date, data_format)
                    colm += 1
                    if ticket.close_date:
                        c_date = datetime.strptime(
                            ticket.close_date, "%Y-%m-%d %H:%M:%S")
                        close_date = datetime.strftime(
                            c_date, '%d-%m-%Y')
                        worksheet.write(
                            row, colm, close_date, data_format)
                    else:
                        worksheet.write(
                            row, colm, ticket.close_date, data_format)
                    colm += 1
                    total_time_float = '%02d:%02d' % (
                        int(ticket.total_time), ticket.total_time % 1 * 60)
                    worksheet.write(
                        row, colm, total_time_float, data_format)
                    colm += 1
                colm = 6
                row += 2
                worksheet.write(row, colm, 'Total', header_format)
                colm += 1

                worksheet.write(row, colm, total_total_time, data_format)
                row += 1
                colm = 0

        workbook.close()
        fp.seek(0)
        result = base64.b64encode(fp.read())
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create(
            {'name': 'helpdesk_report.xlsx', 'datas_fname': 'Helpdesk Ticket Report.xlsx', 'datas': result})
        download_url = '/web/content/' + \
            str(attachment_id.id) + '?download=True'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }
