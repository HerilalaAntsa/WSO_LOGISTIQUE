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
import datetime
from openerp import tools
from openerp import  fields, models, api, osv
import openerp

def str_to_datetime(strdate):
    return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)


# FOURNISSEUR = [
#     ('total', 'TOTAL'),
#     ('jovenna', 'JOVENNA'),
#     ('citerne', 'CITERNE'),
#     ('autre', 'AUTRES')
#         ]


class fleet_fuel(models.Model):
    _inherit = 'fleet.vehicle.log.fuel'

    reste_fleet = openerp.fields.Float(string='Reste avant remplissage')
    demandeur = openerp.fields.Char(string='Demandeur')
    date_fuel = openerp.fields.Datetime(string='Date remplissage')
    code_station = openerp.fields.Char(string='code du station')
    nom_carte = openerp.fields.Char(string='Nom du carte')
    num_carte = openerp.fields.Char(string='Numero de la carte total')
    kilom_compteur = openerp.fields.Float(string='Compteur kilometrique')
    code_station = openerp.fields.Char(string='Code de la station')
    lieu = openerp.fields.Char(string='Lieu ou nom de la station')
    type = openerp.fields.Char(string='Type de remplissage')
    compagnie = openerp.fields.Char(string='Facture de:')
    appoint = openerp.fields.Float(string='Appoint')

    fuel_type = openerp.fields.Selection([('gasoline', 'SP 95'),
                                          ('diesel', 'GAZOLE'),
                                          ('electric', 'Electric'),
                                          ('hybrid', 'Hybrid')], string='Type de carburant', help='Fuel Used by the vehicle')

    vendor_id = openerp.fields.Selection([('total', 'TOTAL'),
                                          ('jovenna', 'JOVENNA'),
                                          ('citerne', 'CITERNE'),
                                          ('autre', 'AUTRES')], 'Fournisseur')

    conducteur_id = openerp.fields.Many2one('fleet.driver', string='Chauffeur')


    _defaults = {
        'use_to_fuel':'t'

    }


    @api.model
    def create(self, values):
        fuel_id = super(fleet_fuel, self).create(values)
        fuel_obj = self.browse(fuel_id)
        cost_id = fuel_obj.cost_id
        qty = fuel_obj.liter
        fournisseur = fuel_obj.vendor_id

        cost_id.write({'litre_quantity':qty,'vendor_id':fournisseur})

        return fuel_id



    @api.onchange('vehicle_id')
    def onchange_info_vehicle(self):
        if not self.vehicle_id:
            return False

        else:
            voiture = self.vehicle_id
            self.unit = voiture.odometer_unit
            self.fuel_type = voiture.fuel_type
            self.conducteur_id = voiture.conducteur_id.id


fleet_fuel()



class fleet_vehicle_card (models.Model):
    _name = 'fleet.vehicle.card'
    _rec_name = 'numero'

    numero = openerp.fields.Char(string='Numero Carte', help='Numero de la carte carburant')
    name = openerp.fields.Char(string='Nom de la carte', help='Nom de la carte carburant', required=True)
    holder_id = openerp.fields.Many2one('res.partner', string='Titulaire')
    plafond = openerp.fields.Float(string='Plafond', help="Plafond")

fleet_vehicle_card()

class fleet_vehicle (models.Model):
    _inherit='fleet.vehicle'

    tagip = openerp.fields.Boolean(string='Tagip ?')
    odometer_tagip = openerp.fields.Float(string='Releve kilometrique tagip')
    card_id = openerp.fields.Many2one('fleet.vehicle.card', string='Carte carburant' )
    name_card = openerp.fields.Char(related='card_id.name', string='Nom Carte', readonly=1 )
    holder_id = openerp.fields.Many2one('res.partner', string='Detenteur')

    fuel_type = openerp.fields.Selection([('gasoline', 'SP 95'),
                                          ('diesel', 'GAZOLE'),
                                          ('electric', 'Electric'),
                                          ('hybrid', 'Hybrid')], string='Fuel Type', help='Fuel Used by the vehicle')

fleet_vehicle()


class fleet_vehicle_cost (models.Model):
    _inherit = 'fleet.vehicle.cost'

    litre_quantity = openerp.fields.Float(string='Litres')
    appoint = openerp.fields.Float(string='Appoint')
    qty_totale = openerp.fields.Float(string='Total carburant consommes')
    use_to_fuel = openerp.fields.Boolean(string='Pour carburant')
    vendor_id = openerp.fields.Selection([('total', 'TOTAL'),
                                          ('jovenna', 'JOVENNA'),
                                          ('citerne', 'CITERNE'),
                                          ('autre', 'AUTRES')], string='Fournisseur')


fleet_vehicle_card()
