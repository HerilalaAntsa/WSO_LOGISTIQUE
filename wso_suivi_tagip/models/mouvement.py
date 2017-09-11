# -*- coding: utf-8 -*-
'''
Created on Aout 2017

@author: Antsa
'''

from odoo import models, fields, api, _
import odoo
from odoo.exceptions import UserError
from odoo.tools.translate import _
from pygments.lexer import _inherit


class Mouvement(models.Model):
    _name = "wso.tagip.report.mouvement"

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicule', required=True)
    date_debut = fields.Char(string='Date de début')
    date_fin = fields.Char(string='Date de fin')
    duree_roulage = fields.Char(string='Durée de roulage')
    dist_parcourue = fields.Char(string='Distance parcourue')
    vitesse_moy = fields.Char(string='Vitesse moyenne')
    vitesse_max = fields.Char(string='Vitesse maximum')
    duree_arret = fields.Char(string='Durée des arrêts')
    nb_arret = fields.Float(string='Nombre d\'arrêt')
    report_id = fields.Many2one('wso.tagip.report', string="Rapport")





