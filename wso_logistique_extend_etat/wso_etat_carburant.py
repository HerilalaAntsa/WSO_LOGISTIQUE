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
Created on 28 Aout 2015

@author: Johary
'''


from openerp.osv import fields, osv
from datetime import date,datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP

from openerp import  fields, models, api
import openerp

class etat_consommation_carburant(models.Model):
    _name = 'etat.consommation.carburant'

    name = openerp.fields.Char(string='Description', default='Suivi et controle consommation carburant')
    from_date = openerp.fields.Date(string='DU')
    to_date = openerp.fields.Date(string='AU')
    suivi_ids = openerp.fields.One2many('fleet.suivi.consommation.temp', 'etat_id', string='Fuels')



    @api.multi
    def get_fuel(self):
        date_debut = self.from_date
        date_fin = self.to_date

        track_pool = self.env['fleet.suivi.consommation.temp']

        #supppression des enregistrements existants d'abord
        track_id_list = track_pool.search([('etat_id','=', self.id)])
        for track_id in track_id_list :
            track_id.write({'etat_id':''})

        #Recherche et agregation
        self.env.cr.execute("""  select t.vehicle_id as vehicle_id,t.marque_vehicle as marque_vehicle, t.conducteur_id as conducteur_id,sum(t.qty_totale) as qty_totale, sum(t.distance) as distance, sum(t.cost_amount) as montant
                        from (
                            select  c.vehicle_id, f.qty_totale, f.kilom_compteur,f.last_kilom,f.distance, f.consommation, f.marque_vehicle, f.conducteur_id, f.cost_amount
                            from fleet_vehicle_log_fuel f, fleet_vehicle_cost c
                            where f.date_fuel>=%s and f.date_fuel<=%s
                            and f.cost_id=c.id
                            order by vehicle_id,kilom_compteur

                        ) as t
                        group by t.vehicle_id, t.marque_vehicle, t.conducteur_id""",(date_debut,date_fin))

        for res in self.env.cr.dictfetchall():
            vehicle_id = res['vehicle_id']
            marque = res['marque_vehicle']
            conducteur_id = res['conducteur_id']
            qty = res['qty_totale']
            kilom = res['distance']
#             km_max = res['km_max']
#             km_min = res['km_min']
            montant = res['montant']
            etat_id = self.id

            #Distance effectue
#             if km_max==km_min:
#                 kilom=km_max
#             else:
#                 kilom=float(km_max)-float(km_min)

            if kilom == 0:
                consommation = 0

            if kilom>0:
                consommation = (float(qty) * 100) / (float(kilom))

            vals = {
                  'vehicle_id':vehicle_id,
                  'name':marque,
                  'conducteur_id':conducteur_id,
                  'qty_fuel':qty,
                  'consommation':consommation,
                  'montant':montant,
                  'kilometrage':kilom,
                  'etat_id':etat_id
            }

            track_pool.create(vals)


#     def get_fuel(self, cr, uid, ids, context=None):
#         fuel_etat_browse=self.browse(cr, uid, ids[0], context=context)
#         date_debut=fuel_etat_browse.from_date
#         date_fin=fuel_etat_browse.to_date
#
#         fuel_pool=self.pool.get('fleet.vehicle.log.fuel')
#
#         #supppression des enregistrements existants d'abord
#         fuel_id_list= fuel_pool.search(cr, uid,[('etat_id','=', ids[0])])
#         for fuel_id in fuel_id_list :
#             fuel_pool.write(cr, uid, fuel_id, {'etat_id':''}, context=context)
#
#         fuel_id_list= fuel_pool.search(cr, uid,[('date_fuel','<=', date_fin), ('date_fuel','>=', date_debut)])
#
#         if fuel_id_list:
#             for fuel_id in fuel_id_list:
#                 fuel_browse=fuel_pool.browse(cr, uid, fuel_id, context=context)
#                 etat_id=fuel_browse.etat_id
#
#                 print("etat_id")
#                 print etat_id
#
#                 fuel_pool.write(cr, uid, fuel_id, {'etat_id':ids[0]}, context=context)


etat_consommation_carburant()

# class fleet_vehicle_log_fuel(osv.osv):
#     _inherit = 'fleet.vehicle.log.fuel'
#     _columns = {
#         'etat_id':fields.many2one('etat.consommation.carburant'),
#     }
# fleet_vehicle_log_fuel()

class fleet_suivi_consommation_temp(models.Model):
    _name = 'fleet.suivi.consommation.temp'

    name = openerp.fields.Char(string='Marque')
    vehicle_id = openerp.fields.Many2one('fleet.vehicle', string='Vehicule')
    conducteur_id = openerp.fields.Many2one('fleet.driver', string='Chauffeur')
    qty_fuel = openerp.fields.Integer(string='Quantite')
    consommation = openerp.fields.Float(string='Consommation')
    montant = openerp.fields.Float(string='Montant Total')
    kilometrage = openerp.fields.Float(string='Kilometrage')
    etat_id = openerp.fields.Many2one('etat.consommation.carburant', string='Etat_id')

fleet_suivi_consommation_temp()
