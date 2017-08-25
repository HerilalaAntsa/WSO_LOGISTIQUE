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
from datetime import date,datetime
from openerp import  fields, models, api
import openerp
from openerp.tools.translate import _
from openerp.exceptions import UserError


class fleet_vehicle_odometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    last_value = openerp.fields.Float(string='Dernier kilometrage', default=0.0)


    @api.onchange('vehicle_id','date')
    def wso_on_change_vehicle(self):
        if not self.date:
            date=datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

        if not self.vehicle_id:
            return False

        if self.vehicle_id:
            vehicle_id = self.vehicle_id
            test_panne = vehicle_id.panne_tableau_kilometrique

            if test_panne == False:
                last_value = self.get_last_value(vehicle_id, date)
            else:
                last_value=vehicle_id.odometer

            self.unit = vehicle_id.odometer_unit
            self.last_value = last_value



    @api.multi
    def get_last_value(self, vehicle_id, date):
        if vehicle_id and date:
            result = 0.0
            self.env.cr.execute("""SELECT MAX(value) as last_value FROM fleet_vehicle_odometer WHERE date<=""""'"+date+"'"""" AND vehicle_id="""+vehicle_id+""" """)
            for x in self.env.cr.dictfetchall():
                last_value = x['last_value']
                result = last_value

        return result


    @api.model
    def create(self, vals):
        vehicle_id = vals.get('vehicle_id')

        fleet_pool = self.pool['fleet.vehicle']
        voiture = fleet_pool.browse(vehicle_id)
        test_panne = voiture.panne_tableau_kilometrique

        last_value = vals.get('last_value')
        kilom_value = vals.get('value')

        if test_panne == False:
            if last_value and last_value!=0.0:
                if kilom_value>last_value:
                    odometer_id = super(fleet_vehicle_odometer, self).create(vals)
                else:
                    raise UserError(_(" Le kilometrage saisi ne doit pas etre inferieur ou egal au dernier kilometrage du vehicule: \n %s Kilometres.") % (str(last_value)))

            else:
                date = vals.get('date')

                if not date:
                    date = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

                dernier_kilometrage = self.get_last_value(vehicle_id, date)
                vals['last_value'] = dernier_kilometrage

                if kilom_value > last_value:
                    odometer_id = super(fleet_vehicle_odometer, self).create(vals)

                else:
                    raise UserError(_(" Le kilometrage saisi ne doit pas etre inferieur ou egal au dernier kilometrage du vehicule: \n %s Kilometres.") % (str(last_value)))


        else:
            dernier_kilometrage = voiture.odometer
            vals['value'] = dernier_kilometrage
            vals['last_value'] = dernier_kilometrage
            odometer_id = super(fleet_vehicle_odometer, self).create(vals)

        return odometer_id


fleet_vehicle_odometer()


class fleet_vehicle_cost(models.Model):
    _inherit = 'fleet.vehicle.cost'

    @api.onchange('liter_quantity', 'appoint')
    def onchange_liter_qty_totale(self):
        self.qty_totale = float(self.liter_quantity) + float(self.appoint)

#     @api.onchange('appoint', 'liter_quantity')
#     def onchange_appoint_qty_totale(self):
#         self.qty_totale = float(self.liter_quantity) + float(self.appoint)

fleet_vehicle_cost()


class fleet_vehicle_log_fuel(models.Model):
    _inherit = 'fleet.vehicle.log.fuel'

    order_id = openerp.fields.Many2one('fuel.order', string='Commande carburant')
    order_line_id = openerp.fields.Many2one('fuel.order.line', string='Ligne de Commande carburant')
    consommation = openerp.fields.Float(string='Consommation')
    last_kilom = openerp.fields.Float(string='Last kilometer')
    distance = openerp.fields.Float(string='Distance effectuee')
    qty_totale = openerp.fields.Float(string='Total carburant consommes')
    marque_vehicle = openerp.fields.Char(string='Marque / Type')
    vehicle_consommation = openerp.fields.Float(string='Consommation normale')


    @api.onchange('vehicle_id')
    def onchange_info_vehicle(self):
        if not self.vehicle_id:
            return False

        else:
            voiture = self.vehicle_id
            self.unit = voiture.odometer_unit
            self.fuel_type = voiture.fuel_type
            self.conducteur_id = voiture.conducteur_id.id
            self.marque_vehicle = voiture.model_id.name
            self.vehicle_consommation =  voiture.consommation
            self.notes = voiture.observation


    @api.model
    def create(self, values):
        odometer_pool = self.pool['fleet.vehicle.odometer']
        fleet_pool=self.pool['fleet.vehicle']

        fuel_vehicle = values.get('vehicle_id')

        fleet_obj = fleet_pool.browse(fuel_vehicle)
        test_panne = fleet_obj.panne_tableau_kilometrique

        fuel_date = values.get('date_fuel')
        if not fuel_date:
            fuel_date = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

        fuel_kilom_value = values.get('odometer')
        last_value = 0.0
        get_last_value = odometer_pool.get_last_value(fuel_vehicle, fuel_date)

        if get_last_value:
            last_value = get_last_value

        values['last_kilom'] = last_value

#         qty=values.get('liter')
        qty = values.get('qty_totale')
        price_unit = values.get('price_per_liter')

        if test_panne == False:
            if fuel_kilom_value > last_value:
                if price_unit>0 and qty>0:
                    distance = float(fuel_kilom_value) - float(last_value)
                    values['distance'] = distance
                    consommation = (float(qty) * 100) / (float(distance))
                    values['consommation'] = consommation
                else:
                    raise UserError(_(" Veuillez remplir correctement les champs Litre et Prix au litre."))
            else:
                raise UserError(_(" Le kilometrage saisi ne doit pas etre inferieur ou egal au dernier kilometrage du vehicule: \n %s Kilometres.") % (str(last_value)))

        if test_panne == True:
            if price_unit>0 and qty>0:
                if not last_value:
                    last_value = 0.0
                values['distance'] = 0.0
                values['consommation'] = 0.0
            else:
                raise UserError(_(" Veuillez remplir correctement les champs Litre et Prix au litre."))

        fuel_id = super(fleet_vehicle_log_fuel, self).create(values)
        self.update_depends(fuel_id)

        return fuel_id

    @api.multi
    def update_depends(self, fuel_id):
        fuel_obj = self.browse(fuel_id)
        cost_id = fuel_obj.cost_id
        odometer_id = cost_id.odometer_id

        date_update = fuel_obj.date_fuel
        last_kilom_update = fuel_obj.last_kilom
        appoint = fuel_obj.appoint
        qty_totale = fuel_obj.qty_totale

        odometer_id.write({'date':date_update, 'last_value':last_kilom_update})
        cost_id.write({'date':date_update, 'qty_totale':qty_totale, 'appoint':appoint})

        return True


    @api.onchange('amount', 'price_per_liter')
    def get_liter_total(self):
        if self.price_per_liter!=0.0:
            if self.amount:
                self.qty_totale = float(self.amount) / float(self.price_per_liter)

    @api.onchange('liter', 'appoint')
    def onchange_liter_qty_totale(self):
        self.qty_totale = float(self.liter) + float(self.appoint)


#     @api.onchange('appoint', 'liter')
#     def onchange_appoint_qty_totale(self):
#         self.qty_totale = float(self.liter) + float(self.appoint)

#     @api.onchange('price_per_liter', 'qty_totale')
#     def onchange_price_per_liter_amount_total(self):
#         self.amount = float(self.price_per_liter) * float(self.qty_totale)


#     @api.onchange('appoint', 'qty_totale', 'liter')
#     def onchange_appoint_liter(self):
#         self.liter = float(self.qty_totale) - float(self.appoint)


    @api.onchange('qty_totale', 'appoint', 'price_per_liter')
    def onchange_qty_totale_amount_total(self):
        self.liter = float(self.qty_totale) - float(self.appoint)
        self.amount = float(self.qty_totale) * float(self.price_per_liter)

fleet_vehicle_log_fuel()
