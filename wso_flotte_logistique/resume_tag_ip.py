# -*- coding: utf-8 -*-
'''
Created on 11 mars 2015

@author: User
'''
from openerp.osv import fields, osv
import time
import datetime
from openerp import tools
from openerp.osv.orm import except_orm
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
def str_to_datetime(strdate):
    return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)

class wso_resume (osv.osv):
    _name = "wso.tag.resume"
    _description = "Resume de chaque vehicule"
#     _columns = {
#         'vehicule':fields.char(string='Vehicule'),
#         'nombre_arret':fields.char(string='Nombre arret'),
#         'date_depart':fields.datetime(string='date et heure du depart'),
#         'longitude_depart':fields.char(string='Longitude'),
#         'latitude_depart':fields.char(string='Latitude'),
#         'lieu_depart':fields.char(string='lieu'),
#         'longitude_arrivee':fields.char(string='longitude '),
#         'latitude_arrivee':fields.char(string='latitude'),
#         'lieu_arrivee':fields.char(string='lieu d arrivee'),
#         'date_arrivee':fields.datetime(string='Date et heure arrivee'),
#         'vitesse_moyenne':fields.char(string='vitese moyenne en Km/h'),
#         'vitesse_maximale':fields.char(string='vitesse maximale en Km/h'),
#         'distance_parcourue':fields.char(string='Distance totale parcourue'),
#         'temps_arret':fields.char(string='Temps d arret'),
#         'remarque': fields.text(string='remarque'),
#         'temps_parcours':fields.char(string='temps du parcours'),
#         'date_liv':fields.datetime(string='Date'),
#                 }

    _columns = {
        'vehicle_id':fields.many2one('fleet.vehicle',string='Vehicule'),
        'nombre_arret':fields.integer(string='Nombre arret'),
        'date_depart':fields.datetime(string='Temps depart'),
        'longitude_depart':fields.integer(string='Longitude'),
        'latitude_depart':fields.integer(string='Latitude'),
        'lieu_depart':fields.char(string='lieu'),
        'longitude_arrivee':fields.integer(string='Longitude '),
        'latitude_arrivee':fields.integer(string='Latitude'),
        'lieu_arrivee':fields.char(string='Lieu arrivee'),
        'date_arrivee':fields.datetime(string='Temps arrivee'),
        'vitesse_moyenne':fields.float(string='Vitesse moyenne (Km/h)', group_operator="max"),
        'vitesse_maximale':fields.float(string='Vitesse maximale (Km/h)', group_operator="max"),
        'distance_parcourue':fields.float(string='Distance totale parcourue'),
        'temps_arret':fields.datetime(string='Temps d arret'),
        'remarque': fields.text(string='Remarque'),
#         'temps_parcours':fields.char(string='Duree du parcours'),
        'duree_parcours' : fields.datetime('Duree du roulage'),
        'duree_arret' : fields.datetime('Duree des arrets'),
        'date_liv':fields.datetime(string='Date'),
                }
wso_resume()