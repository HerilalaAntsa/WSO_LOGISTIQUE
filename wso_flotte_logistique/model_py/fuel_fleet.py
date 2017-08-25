# -*- coding: utf-8 -*-
import datetime
from odoo import tools
from odoo import  fields, models, api, models

def str_to_datetime(strdate):
    return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)

class fleet_vehicle_log_fuel(models.Model):
    _inherit = 'fleet.vehicle.log.fuel'

    reste_fleet = fields.Float(string='Reste avant remplissage')
    demandeur = fields.Char(string='Demandeur')
    date_fuel = fields.Datetime(string='Date remplissage')
    code_station = fields.Char(string='code du station')
    nom_carte = fields.Char(string='Nom du carte')
    num_carte = fields.Char(string='Numero de la carte total')
    kilom_compteur = fields.Float(string='Compteur kilometrique')
    code_station = fields.Char(string='Code de la station')
    lieu = fields.Char(string='Lieu ou nom de la station')
    type = fields.Char(string='Type de remplissage')
    compagnie = fields.Char(string='Facture de:')
    appoint = fields.Float(string='Appoint')

    fuel_type = fields.Selection([('gasoline', 'SP 95'),
                                          ('diesel', 'GAZOLE'),
                                          ('electric', 'Electric'),
                                          ('hybrid', 'Hybrid')], string='Type de carburant', help='Fuel Used by the vehicle')

    vendor_id = fields.Selection([('total', 'TOTAL'),
                                          ('jovenna', 'JOVENNA'),
                                          ('citerne', 'CITERNE'),
                                          ('autre', 'AUTRES')], 'Fournisseur')

    conducteur_id = fields.Many2one('fleet.driver', string='Chauffeur')


    _defaults = {
        'use_to_fuel':'t'

    }


    @api.model
    def create(self, values):
        fuel_id = super(fleet_vehicle_log_fuel, self).create(values)
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


fleet_vehicle_log_fuel()



class fleet_vehicle_card (models.Model):
    _name = 'fleet.vehicle.card'
    _rec_name = 'numero'

    numero = fields.Char(string='Numero Carte', help='Numero de la carte carburant')
    name = fields.Char(string='Nom de la carte', help='Nom de la carte carburant', required=True)
    holder_id = fields.Many2one('res.partner', string='Titulaire')
    plafond = fields.Float(string='Plafond', help="Plafond")

fleet_vehicle_card()

class fleet_vehicle (models.Model):
    _inherit='fleet.vehicle'

    tagip = fields.Boolean(string='Tagip ?')
    odometer_tagip = fields.Float(string='Releve kilometrique tagip')
    card_id = fields.Many2one('fleet.vehicle.card', string='Carte carburant' )
    name_card = fields.Char(related='card_id.name', string='Nom Carte', readonly=1 )
    holder_id = fields.Many2one('res.partner', string='Detenteur')

    fuel_type = fields.Selection([('gasoline', 'SP 95'),
                                          ('diesel', 'GAZOLE'),
                                          ('electric', 'Electric'),
                                          ('hybrid', 'Hybrid')], string='Fuel Type', help='Fuel Used by the vehicle')

fleet_vehicle()


class fleet_vehicle_cost (models.Model):
    _inherit = 'fleet.vehicle.cost'

    litre_quantity = fields.Float(string='Litres')
    appoint = fields.Float(string='Appoint')
    qty_totale = fields.Float(string='Total carburant consommes')
    use_to_fuel = fields.Boolean(string='Pour carburant')
    vendor_id = fields.Selection([('total', 'TOTAL'),
                                          ('jovenna', 'JOVENNA'),
                                          ('citerne', 'CITERNE'),
                                          ('autre', 'AUTRES')], string='Fournisseur')


fleet_vehicle_card()
