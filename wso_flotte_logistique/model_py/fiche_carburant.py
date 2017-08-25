# -*- coding: utf-8 -*-
'''
Created on 25 Avril. 2017

@author: Johary
'''

from odoo import models, fields, api, _
import odoo


class fleet_vehicle_fuel_gestion(models.Model):
    _inherit = "fleet.vehicle.fuel.gestion"

    feuille_de_route_id = fields.Many2one('wso.flotte.route', string='Feuille de route')

