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
from odoo import tools
from odoo import  fields, models, api
import odoo

def str_to_datetime(strdate):
    return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)

# class fleet_vehicle_media(osv.osv):
#     _inherit = 'fleet.vehicle.media'
# fleet_vehicle_media

class fleet_vehicle_type(models.Model):
    _name = 'fleet.vehicle.type'
    _description = 'Type of vehicle'
    _order = 'type asc'
    _rec_name = 'type'

    type = fields.Char(string='Type',size=256,required=True)

class fleet_vehicle_model(models.Model):
    _inherit = 'fleet.vehicle.model'
    type_id = fields.Many2one('fleet.vehicle.type', string='Type')


class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'
    _rec_name = 'license_plate'

#     def _get_image(self, cr, uid, ids, name, args, context=None):
#         result = dict.fromkeys(ids, False)
#         for obj in self.browse(cr, uid, ids, context=context):
#             result[obj.id] = tools.image_get_resized_images(obj.image_vehicle)
#         return result
#
#     def _set_image(self, cr, uid, id, name, value, args, context=None):
#         return self.write(cr, uid, [id], {'image_vehicle': tools.image_resize_image_big(value)}, context=context)

#     image_medium = fields.Binary(compute='_get_image', inverse="_set_image",
#             string="Medium-sized photo", type="binary", multi="_get_image",
#             store = {
#                 'fleet.vehicle': (lambda self, cr, uid, ids, c={}: ids, ['image_vehicle'], 10),
#             },
#             help="Medium-sized logo of the vehicle. It is automatically "\
#                  "resized as a 128x128px image, with aspect ratio preserved. "\
#                  "Use this field in form views or some kanban views.")
#     image_small = fields.Binary(compute='_get_image', inverse="_set_image",
#             string="Smal-sized photo", type="binary", multi="_get_image",
#             store = {
#                 'fleet.vehicle': (lambda self, cr, uid, ids, c={}: ids, ['image_vehicle'], 10),
#             },
#             help="Small-sized photo of the vehicle. It is automatically "\
#                  "resized as a 64x64px image, with aspect ratio preserved. "\
#                  "Use this field anywhere a small image is required.")

#     _columns = {
#         'image_medium': fields.Binary(_get_image, fnct_inv=_set_image,
#             string="Medium-sized photo", type="binary", multi="_get_image",
#             store = {
#                 'fleet.vehicle': (lambda self, cr, uid, ids, c={}: ids, ['image_vehicle'], 10),
#             },
#             help="Medium-sized logo of the vehicle. It is automatically "\
#                  "resized as a 128x128px image, with aspect ratio preserved. "\
#                  "Use this field in form views or some kanban views."),
#         'image_small': fields.Binary(_get_image, fnct_inv=_set_image,
#             string="Smal-sized photo", type="binary", multi="_get_image",
#             store = {
#                 'fleet.vehicle': (lambda self, cr, uid, ids, c={}: ids, ['image_vehicle'], 10),
#             },
#             help="Small-sized photo of the vehicle. It is automatically "\
#                  "resized as a 64x64px image, with aspect ratio preserved. "\
#                  "Use this field anywhere a small image is required."),
#
#     }


    image_vehicle = fields.Binary("Image vehicle")
    image = fields.Binary("Logo",
        help="This field holds the image used as logo for the vehicle, limited to 1024x1024px.")



    num_moteur = fields.Char(string='Numero moteur',size=64)
    date_ammortissement = fields.Date(string='Date ammortissement')
    poids_total_charge = fields.Float(string='Poids total en charge')
    poids_a_vide = fields.Float(string='Poids a vide')
    charge_utile = fields.Float(string='Charge utile')
    proprietaire_id = fields.Many2one('fleet.vehicle.proprietaire', string='Proprietaire')
    date_intervention = fields.Date(string='Derniere intervention')

    partner_id = fields.Many2one('res.partner', string='Proprietaire')
    consommation = fields.Float(string='Consommation au 100 km')
    capacite_res = fields.Char(string='Capacite du reservoir')

    state = fields.Selection([('to_repare','En réparation'),('normal','En circulation'),('out','Sur cale')], string='Etat du vehicule')
    conducteur_id = fields.Many2one('fleet.driver', string='Conducteur')

    is_flotte = fields.Boolean(string='Flotte')
    panne_tableau_kilometrique = fields.Boolean(string='Tableau kilometrique en panne')

    observation = fields.Text(string='Observation')


class fleet_vehicle_model_brand(models.Model):
    _inherit = 'fleet.vehicle.model.brand'

class fleet_vehicle_proprietaire(models.Model):
    _name = 'fleet.vehicle.proprietaire'

    name = fields.Char(string='Proprietaire',size=64)


class fleet_vehicle_state(models.Model):
    _name = "fleet.vehicle.state"
    name = fields.Char(string='Etat',size=64)

class fleet_driver(models.Model):
    _name = "fleet.driver"
    name = fields.Char(string='Chauffeur',size=64)

