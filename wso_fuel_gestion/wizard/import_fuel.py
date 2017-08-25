# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import odoo
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo import  models, api, fields

_logger = logging.getLogger(__name__)


class import_data_fuel(models.Model):
    _name = 'import.data.fuel'
    _rec_name = 'name'

    @api.multi
    def take_column(self):
        view = self.env['ir.model.data'].xmlid_to_res_id('wso_fuel_gestion.view_import_fuel')
        wiz_id = self.env['import.fuel'].create({'import_data_fuel_id': self.id})
        wiz_id.get_column()

        return {
             'name': _('Gestion de carburant'),
             'type': 'ir.actions.act_window',
             'view_type': 'form',
             'view_mode': 'form',
             'res_model': 'import.fuel',
             'views': [(view, 'form')],
             'view_id': view,
             'target': 'new',
             'res_id': wiz_id.id,
         }

    name = fields.Char(string='Nom')
    data = fields.Binary(string='Fichier', required=True)
    filename = fields.Char(string='File Name', required=True)

    date_import = fields.Date(string='Date importation' ,default=fields.Date.context_today)


