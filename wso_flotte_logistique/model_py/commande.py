# -*- coding: utf-8 -*-
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
    lieu = fields.Char(compute='_get_client_street', string='Lieu de livraison')
    facture = fields.Char('N° Facture', size=128, required=True)

@api.multi
@api.onchange('client_id')
def _get_client_street(self):
    for cli in self:
        if cli.client_id:
            lieu = cli.client_id.street

wso_commande()