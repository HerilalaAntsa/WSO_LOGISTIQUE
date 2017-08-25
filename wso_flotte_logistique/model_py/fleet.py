# -*- coding: utf-8 -*-

import datetime
from odoo import tools
from odoo import  fields, models, api
import odoo

def str_to_datetime(strdate):
    return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)

class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'
    _rec_name = 'license_plate'

    feuille_de_route_count = fields.Integer(compute='_compute_feuille_de_route_count', string='# de feuille de route')
    tagip = fields.Boolean(string='TAG-IP ?')
    odometer_tagip = fields.Float(string='Releve kilometrique tagip')
    consommation =  fields.Float(string='Consommation au 100')
    capacite_reservoir = fields.Float(string='Capacité du réservoir')
    fond_de_cuve = fields.Float(string='Fond de cuve')

    fuel_type = fields.Selection([('gasoline', 'SP 95'),
                                  ('diesel', 'GAZOLE'),
                                  ('electric', 'Electric'),
                                  ('hybrid', 'Hybrid')],
                                 string='Type de carburant')

    def _compute_feuille_de_route_count(self):
        fdr = self.env['wso.flotte.route']
        for record in self:
            record.feuille_de_route_count = fdr.search_count([('vehicle_id', '=', record.id)])

fleet_vehicle()