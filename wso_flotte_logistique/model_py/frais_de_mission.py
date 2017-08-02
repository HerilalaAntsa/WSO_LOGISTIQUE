# -*- coding: utf-8 -*-
##############################################################################
#
#    Ce module prendra en charge la d�finition de toutes les d�penses utiles
#    pendant le voyage, par rapport � l'ordre de mission
#
##############################################################################
'''
Created on July 2017

@author: Antsa
'''
from odoo import  fields, models, api


class wso_frais_de_mission (models.Model):
    _name = "wso.flotte.frais.mission"
    _description = u"Toutes les dépenses utiles pendant le voyage, selon l'ordre de mission."

    # Une feuille de route ne pourra avoir qu'un seul frais de mission (aucun doublon)
    feuille_de_route_id = fields.Many2one('wso.flotte.route', string='Feuille de route', required=True)
    date_saisie = fields.Date('Date de saisie', size=128)
    bon_de_paiement = fields.Char('N° BP', size=128)
    ration = fields.Float('Rations')
    frais = fields.Float('Frais')
    hebergement = fields.Float('Hébergement')
    complement_carburant = fields.Float('Complement de carburant')
    indemnite_hs = fields.Float('Indemnite HS')
    autre = fields.Float('Autres')
    note = fields.Text('Notes')

    bareme_contrainte = fields.Boolean(store= False, default= False)
    note_bareme = fields.Char(string='Remarque sur le montant de ration', size=128)

    _sql_constraints = {
                        ('feuille_de_route_unique', 'unique(feuille_de_route_id)', ' Une feuille de route ne doit avoir qu\'un seul frais de mission.')
                    }

    @api.onchange('feuille_de_route_id')
    def get_ration(self):
        if not self.feuille_de_route_id:
            return False
        else:
            self.ration = self.feuille_de_route_id.destination_id.bareme_ration

    @api.constrains('ration')
    def check_bareme(self):
        fdm = self.frais_de_mission_id
        if fdm.ration > fdm.destination_id.bareme_ration:
            self.bareme_contrainte = True
        else:
            self.bareme_contrainte = False

wso_frais_de_mission()