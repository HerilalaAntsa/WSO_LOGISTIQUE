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

'''
Created on July 2017

@author: Antsa
'''
from odoo import  fields, models, api
from bs4 import BeautifulSoup as Soup

import odoo
import urllib2


class distrib_lieu(models.Model):
    _name = "wso.find.lieu"
    _description = "Zone de lieu"

    longitude = fields.Float('Longitude', size=128)
    longitude_max = fields.Float('limite superieur (Longitude)', size=128 )
    latitude = fields.Float('Latitude', size=128)
    latitude_max = fields.Float('limite superieur (Latitude)', size=128 )
#     zone = fields.Related('res.wiso.ville', 'ville_id','zone_id', 'Villes')
    ville_id = fields.Many2one('wso.find.ville', string='Ville de distribution')

    # set by @OnChange(longitude,latitude) :
    lieu = fields.Char('Lieu', size=128, required=True, select=True)
    rue = fields.Char('Rue', size=128)
    region = fields.Char('Région', size=128)
    pays = fields.Char('Pays', size=128)

    type = fields.Selection([
                                ('essence', 'Remplissage essence'),
                                ('livraison', 'client a livrer'),
                                ('repos', 'Divers'),
                                ('inconnu', 'Inconnu')
                            ],
                            string='Type de lieu',
                            default='inconnu',
                            help="Selectionner le statut")

    #    Un fichier XML, décrivant un lieu, sera généré par le site http://nominatim.openstreetmap.org/...
    #    en précisant sa latitude et sa longitude.
    #    L'API BeautifulSoup prendra en charge de le lire et transformera en objet Python
    @api.onchange('longitude','latitude')
    def get_info_localisation(self):
        if not self.longitude or not self.latitude :
            return False

        else:
            self.write({'lieu': '', 'region': '', 'country': ''})
            lat = str(self.latitude)
            lon = str(self.longitude)
            try:
                url = 'http://nominatim.openstreetmap.org/reverse?format=xml&lat='+lat+'&lon='+lon+'&zoom=18&addressdetails=1'
                file = urllib2.urlopen(url)
                print url
                soup = Soup(file.read())
                if soup.find('error'):
                    raise Exception(_(" Impossible de géocoder. \n Veuillez contacter l'administrateur."))
                if soup.find('suburb'):
                    self.lieu = soup.find('suburb').text
                if soup.find('village'):
                    self.lieu = soup.find('village').text
                if soup.find('town'):
                    self.lieu = soup.find('town').text
                if soup.find('fuel'):
                    self.write({'type':'essence'})
                if soup.find('road'):
                    self.rue = soup.find('road').text
                if soup.find('state'):
                    self.region = soup.find('state').text
                if soup.find('country'):
                    self.pays = soup.find('country').text
            except Exception:
                pass

distrib_lieu()

class distrib_ville(models.Model):
    _name = "wso.find.ville"
    _description = "Zone de lieu"
    name = fields.Char(string='Nom de la ville', size=128, default='/')
    bareme_ration = fields.Char(string='Nom de la ville', size=128, default='/')

    _sql_constraints = [('distrib.ville_name_unique','unique(name)', 'Le nom de ville �xiste d�j�')]

distrib_ville()