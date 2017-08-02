# -*- coding: utf-8 -*-
'''
Created on July 2017

@author: Antsa
'''
from odoo import  fields, models
import datetime
from odoo import tools
from odoo.tools.translate import _
from dateutil.relativedelta import relativedelta


def str_to_datetime(strdate):
    return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)


class wso_flotte_arret(models.Model):
    _name = "wso.flotte.arret"
    _description = "Control des_arret de livraison pour la distribution Vidzar"

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicule', required=True)
    date_arret = fields.Datetime('Date de l\'arrêt', size=128)
    numero = fields.Integer('Arret du jour (Ordre)')
    latitude_arret = fields.Float(string='Latitude arrêt', digits=(16, 5))
    longitude_arret = fields.Float(string='Longitude arrêt', digits=(16, 5))
    lieu_id = fields.Many2one('wso.flotte.lieu', string='Lieu de l\'arrêt')
    temps_arret = fields.Char('Duree')
    remarque = fields.Text('Remarque')
    dist_avant = fields.Float('Distance parcourue avant l\'arrêt')
    duree = fields.Datetime('Duree Arret')
    is_depart = fields.Boolean('Départ')
    localisation = fields.Char('Localisation')
    feuille_de_route_id = fields.Many2one('wso.flotte.route', string='Feuille de route')

wso_flotte_arret()