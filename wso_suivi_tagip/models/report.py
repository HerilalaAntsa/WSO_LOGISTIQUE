# -*- coding: utf-8 -*-
'''
Created on Aout 2017

@author: Antsa
'''

from odoo import models, fields, api, _
import odoo
from odoo.exceptions import UserError
from odoo.tools.translate import _


class Report(models.Model):
    _name = "wso.tagip.report"

    @api.multi
    def _get_default_work_for(self):
        work_for = self._context.get('default_work_for')
        if not work_for:
            return False
        return work_for

    name = fields.Char(string='Nom du rapport')
    date = fields.Date(string='Date du rapport')
    frequence = fields.Char(string='Frequence', default='24', readonly=True)
    flotte_type = fields.Selection([
                                        ('DZA.LIV.TNA', 'DZA.LIV.TNA'),
                                        ('DZA.MOTO.TNA', 'DZA.MOTO.TNA'),
                                        ('DZA.SUV.TNA', 'DZA.SUV.TNA'),
                                        ('TOUS', 'TOUS')
                                    ],
                                    default='DZA.LIV.TNA',
                                    string='Categorie de flotte',
                                    help= "Selectionner le type de flotte")


    work_for = fields.Selection([
                                    ('liv', 'DZA.LIV.TNA'),
                                    ('moto', 'DZA.MOTO.TNA'),
                                    ('suv', 'DZA.SUV.TNA')
                                ], string='Flotte', default=_get_default_work_for)


    @api.model
    def create(self, vals):
        vals['name'] = str(vals['date'])
        return super(Report, self).create(vals)


