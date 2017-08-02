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
#
#    Ce module prendra en charge la cr�ation d'un feuille de route qui
#    affichera l'ordre de mission pour chaque v�hicule et chauffeur
#
##############################################################################
'''
Created on July 2017

@author: Antsa
'''
from odoo import  fields, models, api


class wso_commande (models.Model):
    _name = "wso.flotte.commande"
    _description = "Une feuille de route sera composé de un ou plusieurs commandes"

    client_id = fields.Many2one('res.partner', string='Vehicule', required=True)
    feuille_de_route_id = fields.Many2one('wso.flotte.route', string='Feuille de route', required=True)
    date_saisie = fields.Date('Date de saisie', size=128)
    date_arrivee = fields.Datetime('Date et heure d\'arrivée', size=128)
    date_depart = fields.Date('Date et heure de départ', size=128)
    quantite = fields.Integer('Quantité (cageot ou carton)')
    remarque = fields.Text(string='Remarque')
    lieu = fields.Char(string='Lieu de livraison')

@api.onchange('client_id')
def _get_client_streetl(self):
    for cli in self:
        if cli.client_id:
            lieu = cli.client_id.street

wso_commande()