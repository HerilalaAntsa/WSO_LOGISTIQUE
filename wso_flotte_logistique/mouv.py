# -*- coding: utf-8 -*-
'''
Created on 11 mars 2015

@author: User
'''

from openerp.osv import fields, osv
import datetime
from openerp import tools
from openerp.osv.fields import _column
def str_to_datetime(strdate):
    return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)

class wso_feuille_trajet (osv.osv):
    _name = "wso.feu.trajet"
    _description = "Control des arrets de livraison pour la distribution Vidzar"

#     _columns = {
#         'vehicule':fields.char(string='Vehicule', size=128, required=True,),
#         'date_liv':fields.char(string='Date de livraison', size=128),
#         'heure':fields.char(string='Heure de depart', size=128),
#         'latitude':fields.char(string='latitude', size=128),
#         'longitude':fields.char(string='longitude', size=128),
#         'lieu':fields.char(string='lieu', size=128),
#         'temps_parcours':fields.char(string='Duree du trajet', size=128),
#         'remarque': fields.text(string='remarque', size=128),
#         'duree':  fields.char(string='Duree du parcours', size=128),
#         'vitesse':  fields.char(string='Vitesse moyenne en Km/h', size=128),
#         'vitesse_max':  fields.char(string='Vitesse maximale en Km/h', size=128),
#         'etat': fields.char(string='Etat', size=128),
#         'date':fields.datetime(string='Date livraison', size=128),
#         'dist_parc':fields.char(string='distance parcourue', size=128),
#
#                 }
#
    _columns = {
        'vehicle_id':fields.many2one('fleet.vehicle',string='Vehicule', size=128, required=True),
        'date_liv':fields.datetime(string='Date de livraison'),
#         'heure':fields.char(string='Heure de depart', size=128),
        'latitude':fields.float(string='Latitude'),
        'longitude':fields.float(string='Longitude'),
        'lieu':fields.char(string='Lieu', size=128),
        'temps_parcours':fields.datetime(string='Duree du trajet'),
        'remarque': fields.text(string='remarque', size=128),
        'duree':  fields.datetime(string='Duree du parcours'),
        'vitesse':  fields.float(string='Vitesse moyenne (Km/h)', group_operator='avg'),
        'vitesse_max':  fields.float(string='Vitesse maximale (Km/h)'),
        'etat': fields.char(string='Etat', size=128),
        'date':fields.datetime(string='Date livraison'),
        'dist_parc':fields.float(string='Distance parcouru'),
                }

wso_feuille_trajet()

class fleet_vehicle_odometer_tagip (osv.Model):
    _name = 'fleet.vehicle.odometer.tagip'

    _description = 'Logs des differentes variations tagip'

    def _vehicle_log_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            name = record.vehicle_id.name
            if not name:
                name = record.date
            elif record.date:
                name += ' / '+ record.date
            res[record.id] = name
        return res

    _columns = {
        'name': fields.function(_vehicle_log_name_get_fnc, type="char", string='Name', store=True),
        'date': fields.date('Date'),
        'distance_parcourue' : fields.float('Distance parcourue'),
        'value': fields.float('Releve kilometrique', group_operator="max"),
        'vehicle_id': fields.many2one('fleet.vehicle', 'Vehicle', required=True),
                }