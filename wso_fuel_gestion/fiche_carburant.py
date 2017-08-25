# -*- coding: utf-8 -*-
'''
Created on 25 Avril. 2017

@author: Johary
'''

from odoo import models, fields, api, _
import odoo
from odoo.exceptions import UserError
from odoo.tools.translate import _


class fleet_vehicle_fuel_gestion(models.Model):
    _name = "fleet.vehicle.fuel.gestion"

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicule', required=True)
    date_fuel = fields.Date(string='Date', required=True)
    beneficiaire = fields.Char(string='Beneficiaire')
    kilometrage = fields.Float(string='Km')
    amount_fuel = fields.Float(string='Montant')
    price_per_liter = fields.Float(string='P.U')
    qty_fuel = fields.Float(string='Qte en Litre')
    hour_fuel = fields.Float(string='Heure')
    partner_id = fields.Many2one('res.partner', string='Societe / Service')
    libelle_fuel = fields.Char(string='Libelle')
    order_number = fields.Char(string='BC')
    invoice_number = fields.Char(string='Num. Facture')
    panne_tableau = fields.Boolean(string='Panne tableau?')
    tag_ip = fields.Float(string='TAG IP')
    complement_fuel = fields.Float(string='Complement carburant especes')
    consommation_vehicle = fields.Float(string='Consommation au 100Km')


    @api.onchange('panne_tableau')
    def reset_kilom_panne(self):
        if self.panne_tableau == True:
            self.kilometrage = 0.0
        else:
            self.tag_ip = 0.0

    @api.onchange('qty_fuel')
    def onchange_consommation_vehicle(self):
        qty = self.qty_fuel
        tg = self.tag_ip
        km = self.kilometrage
        pu = self.price_per_liter

        if pu > 0:
            self.amount_fuel = float(pu) * float(qty)

        if qty > 0:
            dtf = self.date_fuel
            if self.panne_tableau == True:
                if tg > 0:
                    self._cr.execute("""
                        select max(tag_ip) as distance from fleet_vehicle_fuel_gestion where to_char(date_trunc('day',date_fuel), 'YYYY-MM-DD')<=""""'"+dtf+"'"""" and vehicle_id="""+str(self.vehicle_id.id)+"""
                    """)
                    for x in self._cr.dictfetchall():
                        di = x['distance']
                        if not di:
                            di = 0

                    if tg < di:
                        raise UserError(_(" Veuillez vérifier votre saisie car l'ancienne valeur kilométrique relevée pour ce véhicule /s est de %s km, \n or la saisie que vous essayez de faire est inférieure à cette ancienne valeur. ") % (self.vehicle_id.license_plate, di))
                    else:
                        self.consommation_vehicle = (float(qty) * 100) / (float(tg) - float(di))

            else:
                if km > 0:
                    self._cr.execute("""
                        select max(kilometrage) as distance from fleet_vehicle_fuel_gestion where to_char(date_trunc('day',date_fuel), 'YYYY-MM-DD')<=""""'"+dtf+"'"""" and vehicle_id="""+str(self.vehicle_id.id)+"""
                    """)
                    for x in self._cr.dictfetchall():
                        di = x['distance']
                        if not di:
                            di = 0

                    if km < di:
                        raise UserError(_(" Veuillez vérifier votre saisie car l'ancienne valeur kilométrique relevée pour ce véhicule /s est de %s km, \n or la saisie que vous essayez de faire est inférieure à cette ancienne valeur. ") % (self.vehicle_id.license_plate, di))
                    else:
                        self.consommation_vehicle = (float(qty) * 100) / (float(km) - float(di))




