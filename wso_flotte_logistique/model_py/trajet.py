# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
'''
Created on July 2017

@author: Antsa
'''

from odoo import  fields, models, api

class wso_flotte_trajet(models.Model):
    _name = "wso.flotte.trajet"
    _description = "Control de livraison pour la distribution Vidzar"

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicule', required=True)
    date_trajet = fields.Datetime('Date du trajet', size=128)
    latitude_trajet = fields.Float(string='Latitude trajet', digits=(16, 5))
    longitude_trajet = fields.Float(string='Longitude trajet', digits=(16, 5))
    distance_parcourue = fields.Float('Distance parcourue')
    vitesse_moyenne = fields.Float('Vitesse moyenne (Km/h)')
    vitesse_max = fields.Float('Vitesse maximale (Km /h)')
    lieu_id = fields.Many2one('wso.distrib.lieu', string='Lieu de départ')
    remarque = fields.Text('Remarque')
    duree = fields.Datetime('Duree Arret')
    localisation = fields.Char('Localisation')
    feuille_de_route_id = fields.Many2one('wso.flotte.route', string='Feuille de route')

wso_flotte_trajet()