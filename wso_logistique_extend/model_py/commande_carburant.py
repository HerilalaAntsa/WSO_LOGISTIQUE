# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny S_prepare_order_pickingPRL (<http://tiny.be>).
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
##
##############################################################################
from Tkconstants import LAST
'''
Created on 14 Août. 2015

@author: Johary
'''
import time
from datetime import date,datetime
from openerp.tools.translate import _
from openerp.exceptions import UserError

from openerp import  fields, models, api
import openerp


class fuel_order(models.Model):
    _name='fuel.order'
    _table = 'fuel_order'

#     def _fuel_logs_count(self, cr, uid, ids, field_name, arg, context=None):
#         total = {}
#         for order_id in ids:
#             sub_total=0.0
#             ac_obj = self.pool.get('fleet.vehicle.log.fuel')
#             ac_obj_ids= ac_obj.search(cr, uid,[('order_id','=',order_id)], context=context)
#             for rec in ac_obj.browse(cr,uid,ac_obj_ids,context=context):
#                 sub_total +=1
#             total[order_id] = sub_total
#         return total

    @api.multi
    def _fuel_logs_count(self):
        for fuel_order in self:
            sub_total = 0.0
            ac_obj = self.pool['fleet.vehicle.log.fuel']
            ac_obj_ids= ac_obj.search([('order_id','=',fuel_order.id)])
            for rec in ac_obj.browse(ac_obj_ids):
                sub_total +=1
            fuel_order.sales_count = sub_total

    @api.multi
    def action_view_fuel(self):
        self.ensure_one()
        action = self.env.ref('fleet.fleet_vehicle_log_fuel_act')

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': "{'search_default_order_id': " + ','.join(map(str, self.ids)) + "}",
            'res_model': action.res_model,
            'domain': [('order_id', '=', self.id)],
        }


#     def action_view_fuel(self, cr, uid, ids, context=None):
#         result = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, 'fleet.fleet_vehicle_log_fuel_act', raise_if_not_found=True)
#         result = self.pool['ir.actions.act_window'].read(cr, uid, [result], context=context)[0]
#         result['domain'] = "[('order_id','in',[" + ','.join(map(str, ids)) + "])]"
#         return result


    name = openerp.fields.Char(string='Besoin', size=64, required=True, select=True, default='/')
    date_order = openerp.fields.Date(string='Date de la commande', default=lambda *a: time.strftime('%Y-%m-%d'))
    date_confirmation = openerp.fields.Date(string='Confirmation de la demande')
    date_validation = openerp.fields.Date(string='Validation de la demande')
    date_fin = openerp.fields.Date(string='Fermeture de la commande')
    responsable = openerp.fields.Char(string='Responsable')
    fuel_order_ids = openerp.fields.One2many('fuel.order.line', 'fuel_order_id', string='Order Lines')

    state = openerp.fields.Selection([('draft', 'Nouveau'),
                                      ('confirmed', 'Confirmé'),
                                      ('open', 'En cours'),
                                      ('done', 'Terminé'),
                                      ('cancel', 'Annulé')], string='State', default='draft')

    fuel_logs_count = openerp.fields.Integer(compute='_fuel_logs_count', string='# Fuel')
    notes = openerp.fields.Text(string='Notes')
    partner_id = openerp.fields.Many2one('res.partner', string='Groupe',store=True)

    vendor_id = openerp.fields.Selection([('total', 'TOTAL'),
                                          ('jovenna', 'JOVENNA'),
                                          ('citerne', 'CITERNE'),
                                          ('autre', 'AUTRES')], string='Fournisseur', default='jovenna')



    @api.multi
    def get_partner(self, ids):
        self.env.cr.execute("""
            select id from res_partner where name like '%VIDZAR%'
            """)
        for res in self.env.cr.dictfetchall():
            partner_id = res['id']
        result = partner_id
        return result

    @api.model
    def create(self, vals):
        if vals.get('name','/') == '/':
            vals['name'] = self.pool['ir.sequence'].get('fuel.order') or '/'

        fuel_id = super(fuel_order, self).create(vals)
        partner_id = self.get_partner(fuel_id)
        if partner_id:
            self.write({'partner_id':partner_id})

        return fuel_id


    @api.multi
    def confirm_order(self):
        date = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        order_lines = self.fuel_order_ids

        if order_lines:
            for order_id in order_lines:
                order_id.write({'state':'confirmed'})

        return self.write({'state':'confirmed', 'date_confirmation':date})


    @api.multi
    def validate_order(self):
        date = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        order_lines = self.fuel_order_ids

        if order_lines:
            for order_id in order_lines:
                order_id.write({'state':'open'})

        return self.write({'state':'open', 'date_validation':date})



    @api.multi
    def set_done_order(self):
        date = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        return self.write({'state':'done', 'date_fin':date})

    @api.multi
    def action_cancel(self):
        order_lines = self.fuel_order_ids
        if order_lines:
            for order_id in order_lines:
                order_id.write({'state':'cancel'})
        return self.write({'state':'cancel'})


fuel_order()

class fuel_order_line(models.Model):
    _name='fuel.order.line'
    _table = 'fuel_order_line'

    name = openerp.fields.Text(string='Description')
    date_planned = openerp.fields.Date(string='Date prevue', default=lambda *a: time.strftime('%Y-%m-%d'))
    date_livraison = openerp.fields.Date(string='Date de la livraison')
    qty_demandee = openerp.fields.Char(string='Quantite demandee')
    qty_prise = openerp.fields.Float(string='Quantite prise')
    vehicle_id = openerp.fields.Many2one('fleet.vehicle', string='Vehicule')
    entity = openerp.fields.Char(string='Service/Societe')
    demandeur = openerp.fields.Char(string='Demandeur')
    pompiste = openerp.fields.Char(string='Pompiste')
    conducteur_id = openerp.fields.Many2one('fleet.driver', string='Chauffeur')
    fuel_order_id = openerp.fields.Many2one('fuel.order', string='Commande carburant')
    price_per_liter = openerp.fields.Float(string='Prix au litre')
    montant = openerp.fields.Float(string='Prix total')
    state = openerp.fields.Selection([('draft', 'Nouveau'),
                                      ('confirmed', 'Confirmé'),
                                      ('open', 'En cours'),
                                      ('done', 'Livré'),
                                      ('cancel', 'Annulé')], string='State', default='draft')

    fuel_type = openerp.fields.Selection([('gasoline', 'SP 95'),
                                          ('diesel', 'GAZOLE'),
                                          ('electric', 'Electric'),
                                          ('hybrid', 'Hybrid')], string='Type de carburant')

    odometer = openerp.fields.Float(string='Kilometrage')
    appoint = openerp.fields.Float(string='Appoint')
    qty_totale = openerp.fields.Float(string='Total carburant consommes')

    marque_vehicle = openerp.fields.Char(string='Marque / Type')
    vehicle_consommation = openerp.fields.Float(string='Consommation normale')




    @api.onchange('vehicle_id')
    def get_info_vehicule(self):
        if not self.vehicle_id:
            return False

        else:
            voiture = self.vehicle_id
            odometer_panne = voiture.panne_tableau_kilometrique
            observation = voiture.observation

            if odometer_panne == True:
                if not observation:
                    observation = 'Tableau kilometrique hors service'

            self.conducteur_id = voiture.conducteur_id.id
            self.odometer = voiture.odometer
            self.name = observation
            self.marque_vehicle = voiture.model_id.name
            self.vehicle_consommation = voiture.consommation


    @api.onchange('montant', 'price_per_liter')
    def get_liter(self):
        if self.price_per_liter == 0.0:
            return False

        else:
            if self.montant:
                self.qty_totale = float(self.montant) / float(self.price_per_liter)


    @api.onchange('qty_prise', 'price_per_liter')
    def onchange_montant(self):
        self.montant = float(self.price_per_liter) * float(self.qty_prise)


    @api.onchange('liter_quantity', 'appoint')
    def onchange_liter_qty_totale(self):
            self.qty_totale = float(self.qty_totale) + float(self.appoint)

#     @api.onchange('appoint', 'liter_quantity')
#     def onchange_appoint_qty_totale(self):
#         self.qty_totale = float(self.liter_quantity) + float(self.appoint)


    def _prepare_log_fuel(self, cr, uid, project, last_value, context=None):
        if not last_value:
            last_value = 0.0

        prj = self.browse(cr, uid, project[0], context=context)
        if context is None:
            context = {}
        date = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

        fleet_obj = prj.vehicle_id
        vehicle_id = fleet_obj.id
        kilom_value = prj.odometer
        qty = prj.qty_prise
        appoint = prj.appoint
        qty_totale = prj.qty_totale

        test_panne = fleet_obj.panne_tableau_kilometrique
        marque = fleet_obj.model_id.name
        consommation_vehicle = fleet_obj.consommation

        if test_panne == True:
            kilom_value = fleet_obj.odometer
            consommation = 0.0
            distance = 0.0

        if test_panne == False:
            if kilom_value > last_value:
                distance = float(kilom_value) - float(last_value)
                consommation = (float(qty)*100) / (float(distance))

        prj_vals = {
            'notes': prj.name or '',
            'purchaser_id': prj.fuel_order_id.partner_id.id,
            'date_fuel': date,
            'inv_ref': prj.fuel_order_id.name,
            'vendor_id': prj.fuel_order_id.vendor_id,

            'vehicle_id': vehicle_id,
            'conducteur_id': prj.conducteur_id.id,
            'demandeur': prj.demandeur,

            'fuel_type': prj.fuel_type,
            'liter': qty,
            'price_per_liter': prj.price_per_liter,
            'amount': prj.montant,

            'order_id': prj.fuel_order_id.id,
            'order_line_id': prj.id,

            'consommation':consommation,
            'odometer':kilom_value,
            'last_kilom':last_value,
            'appoint':appoint,

            'qty_totale':qty_totale,
            'distance':distance,
            'marque_vehicle':marque,
            'vehicle_consommation':consommation_vehicle,
        }


        return prj_vals


    @api.cr_uid_ids_context
    def return_action_to_open_fuel(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        if context.get('xml_id'):
            if context.get('xml_id') == 'fleet_vehicle_log_fuel_act':

                log_fuel_pool = self.pool['fleet.vehicle.log.fuel']
                fuel_order_line = self.browse(cr, uid, ids[0], context)
                fuel_order_id = fuel_order_line.fuel_order_id
                state_commande = fuel_order_id.state

                if state_commande == 'done':
                    raise UserError(_(" Cette action ne peut plus aboutir car le Bon de commande est deja termine. \n Veuillez contacter l'administrateur."))

                else:
                    qty_prise = fuel_order_line.qty_prise
                    price_unit = fuel_order_line.price_per_liter

                    kilom = fuel_order_line.odometer
                    test_panne = fuel_order_line.vehicle_id.panne_tableau_kilometrique
                    fuel_order_line_date = fuel_order_line.date_planned
                    vehicle_id = fuel_order_line.vehicle_id.id

                    last_value = 0.0
                    get_last_value = self.env['fleet.vehicle.odometer'].get_last_value(vehicle_id, fuel_order_line_date)
                    if get_last_value:
                        last_value = get_last_value
#
                    if test_panne == False:
                        if kilom > last_value:
                            if qty_prise>0 and price_unit>0:
                                inv = self._prepare_log_fuel(cr, uid, ids, last_value, context=context)
                                log_fuel_pool.create(cr, uid, inv, context=context)
                                date = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
                                self.write(cr, uid, ids[0], {'state':'done', 'date_livraison':date}, context=context)
                            else:
                                raise UserError(_(" Veuillez saisir la quantite transferee ainsi que le prix avant d'effectuer cette action."))
                        else:
                            raise UserError(_(" Le dernier releve kilometrique du vehicule %s est de %s Kilometres. \n Veuillez saisir un kilometrage superieur a cette derniere valeur.") % (fuel_order_line.vehicle_id.license_plate, str(last_value)))

                    else:
                        kilom = last_value
                        if qty_prise>0 and price_unit>0:
                            inv = self._prepare_log_fuel(cr, uid, ids, last_value, context=context)
                            log_fuel_pool.create(cr, uid, inv, context=context)
                            date = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
                            self.write(cr, uid, ids[0], {'state':'done', 'date_livraison':date}, context=context)
                        else:
                            raise UserError(_(" Veuillez saisir la quantite transferee ainsi que le prix avant d'effectuer cette action."))

        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
                }

fuel_order_line()
