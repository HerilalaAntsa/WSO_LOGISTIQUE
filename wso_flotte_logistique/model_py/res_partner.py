# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, exceptions, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def modify_partner_from_map(self, values, id, modif_totale):
        if not id:
            raise exceptions.Warning(_(
                'Partenaire introuvable.'))
        if modif_totale :
            default_fields = ['street', 'street2',
                              'city', 'zip', 'country_id', 'state_id',
                              'partner_latitude',
                              'partner_longitude']
        else:
            default_fields = ['partner_latitude',
                              'partner_longitude']
        partner_id = self.env['res.partner'].browse(id)
        if isinstance(values, dict) and any(
                val in default_fields for val in values.keys()):
            partner_id.write(values)
            return partner_id.id
        else:
            return False
