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
from openerp.osv import fields, osv
from datetime import date,datetime
from openerp.tools.translate import _
from openerp.exceptions import UserError
from openerp import  fields, models, api
import openerp



class fleet_vehicle_log_fuel(models.Model):
    _inherit = 'fleet.vehicle.log.fuel'

    state = openerp.fields.Selection([('draft', 'Nouveau'),
                                     ('done', 'Confirmé'),
                                     ('paid', 'Règlé')], string='Quantite', default='draft')

    date_validation = openerp.fields.Date(string='Date de validation')


    @api.multi
    def set_validate(self):
        cost_obj = self.cost_id
        cost_id = cost_obj.id

        odometer_obj = cost_obj.odometer_id
        odometer_id = odometer_obj.id

        #info sur fleet_vehicle_cost
        cost_amount = cost_obj.amount

        #info sur fleet_vehicle_odometer
#         last_kilom=odometer_obj.last_value
        last_kilom = self.last_kilom
#         kilom_value=odometer_obj.value
#         vehicle_id=odometer_obj.vehicle_id.id

        fleet_obj = self.vehicle_id
        vehicle_id = fleet_obj.id

        #info sur fleet_vehicle_log_fuel
        date_validation = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        date_fuel = self.date_fuel
        liter_qty = self.liter
        fournisseur = self.vendor_id
        prix = self.price_per_liter
        fuel_type = self.fuel_type
        qty_totale = self.qty_totale
        appoint = self.appoint
        acheteur = self.purchaser_id.id
        notes = self.notes
        conducteur_id = self.conducteur_id.id
        kilom_value = self.kilom_compteur

        test_panne = fleet_obj.panne_tableau_kilometrique
        test_privilege = fleet_obj.oublie_kilom

        if test_privilege == False:
            if test_panne == False:
                if kilom_value > last_kilom:
                    distance = float(kilom_value) - float(last_kilom)
                    consommation = (float(qty_totale) * 100) / (float(distance))
                else:
                    raise UserError(_(" Le kilometrage saisi ne doit pas etre inferieur ou egal au dernier kilometrage du vehicule: \n %s Kilometres.") % (str(last_kilom)))

            else:
                distance = 0.0
                consommation = 0.0

        else:
            distance = 0.0
            consommation = 0.0
            kilom_value = 0.0


        odometer_vals = {
            'vehicle_id':vehicle_id,
            'value':kilom_value,
            'date':date_fuel,
            'last_value':last_kilom
        }

        cost_vals = {
            'vehicle_id':vehicle_id,
            'odometer_id':odometer_id,
            'amount':cost_amount,
            'date':date_fuel,
            'liter_quantity':liter_qty,
            'vendor_id':fournisseur,
            'qty_totale':qty_totale,
            'appoint':appoint,
            'odometer_id':odometer_id
        }

        fuel_vals = {
            'state':'done',
            'date_validation':date_validation,
            'liter':liter_qty,
            'purchaser_id':acheteur,
            'notes':notes,
            'vendor_id':fournisseur,
            'cost_amount':cost_amount,
            'price_per_liter':prix,
            'fuel_type':fuel_type,
            'appoint':appoint,
            'date_fuel':date_fuel,
            'conducteur_id':conducteur_id,
            'consommation':consommation,
            'last_kilom':last_kilom,
            'qty_totale':qty_totale,
            'distance':distance,
            'kilom_compteur':kilom_value,
            'cost_id':cost_id
        }

        odometer_obj.write(odometer_vals)
        cost_obj.write(cost_vals)
        return self.write(fuel_vals)


    @api.onchange('date_fuel', 'vehicle_id')
    def onhange_date_fuel(self):
        if self.date_fuel:
            if self.vehicle_id:
                self.last_kilom = self.pool['fleet.vehicle.odometer'].get_last_value(self.vehicle_id.id, self.date_fuel)


fleet_vehicle_log_fuel()



class fleet_vehicle_log_fuel_groups(osv.osv_memory):
    _name = "fleet.vehicle.log.fuel.groups"
    _description = "fleet vehicle log fuel group"

    fuel_id = openerp.fields.Many2one('fleet.vehicle.log.fuel', string='log_fuel')


    @api.multi
    def found_last_value(self, vehicle_id, date, kilom_compteur):
        if vehicle_id and date:

            date_search = str(date)
            date_search = "'"+date_search+"'"

            self.env.cr.execute("""SELECT count(id) as nbr FROM fleet_vehicle_odometer WHERE date=%s AND vehicle_id=%s""",(date_search,vehicle_id))
            for n in self.env.cr.dictfetchall():
                nb_meme_date=n['nbr']

            if nb_meme_date < 1 or nb_meme_date == 1:
                self.env.cr.execute("""SELECT MAX(value) as last_value FROM fleet_vehicle_odometer WHERE date<%s AND vehicle_id=%s""",(date_search, vehicle_id))
                for x in self.env.cr.dictfetchall():
                    last_value = x['last_value']
                    result = last_value

                    if not result:
                        self.env.cr.execute("""SELECT MAX(last_value) as last_value FROM fleet_vehicle_odometer WHERE date<=%s AND vehicle_id=%s""",(date_search, vehicle_id))
                        for y in self.env.cr.dictfetchall():
                            last_val = y['last_value']
                            res = last_val

                        if res:
                            result = res
                        else:
                            result = 0.0

            else:
                self.env.cr.execute("""SELECT MAX(date) as date_max FROM fleet_vehicle_odometer WHERE date<=%s AND vehicle_id=%s""",(date_search, vehicle_id))
                for y in self.env.cr.dictfetchall():
                    date_max = y['date_max']

                if kilom_compteur:
                    self.env.cr.execute("""SELECT MAX(value) as last_value FROM fleet_vehicle_odometer WHERE date=%s AND vehicle_id=%s""",(date_max, vehicle_id))
                    for val_max in self.env.cr.dictfetchall():
                        vx = val_max['last_value']

                    self.env.cr.execute("""SELECT MIN(value) as last_value FROM fleet_vehicle_odometer WHERE date=%s AND vehicle_id=%s""",(date_max, vehicle_id))
                    for val_min in self.env.cr.dictfetchall():
                        vn = val_min['last_value']

                    if kilom_compteur == vx:
                        result = vn

                    else:
                        self.env.cr.execute("""SELECT MAX(value) as last_value FROM fleet_vehicle_odometer WHERE date<%s AND vehicle_id=%s""",(date_search, vehicle_id))
                        for v in self.env.cr.dictfetchall():
                            last_value = v['last_value']
                            result = last_value

                            if not result:
                                self.env.cr.execute("""SELECT MAX(last_value) as last_value FROM fleet_vehicle_odometer WHERE date<=%s AND vehicle_id=%s""",(date_search, vehicle_id))
                                for z in self.env.cr.dictfetchall():
                                    last_val = z['last_value']
                                    res = last_val

                                if res:
                                    result = res
                                else:
                                    result = 0.0

        return result


    @api.multi
    @api.cr_uid_ids_context
    def actualisation(self, cr, uid, ids, context):
        fuel_pool = self.env['fleet.vehicle.log.fuel']

        nbr_active_ids = len(context['active_ids'])
        tab_active_ids = context['active_ids']

        i=1
        while i <= nbr_active_ids:
            id_list = tab_active_ids[nbr_active_ids-i]
            fuel_obj = fuel_pool.browse(cr, uid, id_list)
            date_fuel = fuel_obj.date_fuel
            vehicle_id = fuel_obj.vehicle_id.id
            kilom_compteur = fuel_obj.kilom_compteur

#             last_kilom=odometer_pool.get_last_value(cr, uid, vehicle_id, date_fuel, context)
            last_kilom = self.found_last_value(vehicle_id, date_fuel, kilom_compteur)

            fuel_last_kilom = fuel_obj.last_kilom
            qty_totale = fuel_obj.qty_totale

            if last_kilom != fuel_last_kilom:
                kilom = fuel_obj.kilom_compteur

                if last_kilom:
                    if last_kilom<kilom and kilom>0:
                        distance = float(kilom) - float(last_kilom)
                        consommation = (float(qty_totale) * 100) / float(distance)

                    else:
                        distance = 0.0
                        consommation = 0.0

                else:
                    last_kilom = 0.0
                    if kilom>0:
                        distance = float(kilom) - float(last_kilom)
                        consommation = (float(qty_totale) * 100) / float(distance)
                    else:
                        distance = 0.0
                        consommation = 0.0

                odometer_id = fuel_obj.cost_id.odometer_id
                odometer_id.write({'last_value':last_kilom})

                fuel_vals = {
                    'last_kilom':last_kilom,
                    'distance':distance,
                    'consommation':consommation
                }
                fuel_obj.write(fuel_vals)

            else:
                if last_kilom < kilom_compteur:
                    distance = float(kilom_compteur) - float(last_kilom)
                    consommation = (float(qty_totale) * 100) / float(distance)
                    fuel_vals = {
                        'distance':distance,
                        'consommation':consommation
                    }
                    fuel_obj.write(fuel_vals)

            i = i+1

        return True

fleet_vehicle_log_fuel_groups()


