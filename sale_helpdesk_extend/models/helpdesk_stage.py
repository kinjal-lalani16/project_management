# -*- coding: utf-8 -*-
# © 2018-Today Tundra Consulting & Advisory (http://tundra-consulting.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HelpdeskStage(models.Model):
    """Inherited Helpdesk Stage."""

    _inherit = 'helpdesk.stage'

    is_solved = fields.Boolean(string="Solved")

    @api.multi
    @api.constrains('is_solved')
    def _check_state(self):
        '''
        This method is used to check the stage and raise Error
        if more than one stage is set to True in the
        'Is Solved' boolean field.
        ----------------------------------------------------
        @param self: object pointer
        '''
        if self.is_solved == True:
            stage = self.search([('is_solved', '=', True)])
            remove_current = [current_stage for current_stage in stage if current_stage.id != self.id]
            if remove_current:
                raise ValidationError(_('You cannot activate more than one Solved stage.'))