# -*- coding: utf-8 -*-
##############################################################################
#
#    Ce module prendra en charge la création d'un feuille de route qui
#    affichera l'ordre de mission pour chaque véhicule et chauffeur
#
##############################################################################
'''
Created on July 2017

@author: Antsa
'''
from odoo import  fields, models, api, exceptions
import datetime
from odoo import tools
from odoo.tools.translate import _


def str_to_datetime(strdate):
    return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)


class wso_flotte_route(models.Model):
    _name = "wso.flotte.route"
    _description = "Ordre de mission pour la livraison de la distribution Vidzar"

    name = fields.Text(string='Référence feuille de route')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicule', required=True)
    conducteur_id = fields.Many2one('fleet.driver', string='Conducteur')    # set by a @OnChange('vehicule_id')

    responsable_zone = fields.Char('Responsable zone', size=128)
    commercial = fields.Char('Commercial', size=128)
    mobile_1 = fields.Char('Mobile 1', size=128)
    mobile_2 = fields.Char('Mobile 2', size=128)

    date_saisie = fields.Date('Date de saisie', size=128, default=fields.Date.context_today)
    date_depart_prevue = fields.Date('Date de départ prévu', size=128)
    date_retour_prevue = fields.Date('Date de retour prévu', size=128)
    date_depart = fields.Date('Date de départ', size=128)
    date_retour = fields.Date('Date de retour', size=128)

    destination_id = fields.Many2one('wso.flotte.destination', string='Destination', required=True)
    passager = fields.Integer('Nombre de passagers', readonly=True,)
    total_distance = fields.Float(string='Distance totale (km)')
    marge_km = fields.Float(string='Marge (km)')
    estimation_litre = fields.Float(compute='_compute_estimation_litre', string='Estimation de quantité de carburant (l)')
    type_mission = fields.Selection([
                                        ('livraison', 'Livraison'),
                                        ('transport', 'Transport personnels')
                                    ],
                                    default='livraison',
                                    string='Mission',
                                    help= "Selectionner le type de mission")

    state = fields.Selection([('draft', 'Nouveau'),
                                  ('confirmed', 'Confirmé'),
                                  ('open', 'En cours'),
                                  ('done', 'Terminé'),
                                  ('cancel', 'Annulé')],
                             string='Etat', default='draft', readonly=True, copy=False)

    marque_vehicle = fields.Char(string='Marque / Type', compute="_get_vehicule_detail", store= False)

    # Les mouvements (arret/trajet) d'un vehicule ne s'afficheront que 'state = en cours'
    commande_ids = fields.One2many('wso.flotte.commande', 'feuille_de_route_id', string='Ordre de mission')
    arret_ids = fields.One2many('wso.flotte.arret', 'feuille_de_route_id', string='Liste des arrêts')
    trajet_ids = fields.One2many('wso.flotte.trajet', 'feuille_de_route_id', string='Liste des trajets')
    # Une feuille de route ne pourra avoir qu'un seul frais de mission (aucun doublon) : cf 'frais_de_mission.py'
    frais_de_mission_ids = fields.One2many('wso.flotte.frais.mission', 'feuille_de_route_id', string='Frais de mission')

    fiche_carburant_ids = fields.One2many('fleet.vehicle.fuel.gestion', 'feuille_de_route_id', string='Fiche de carburant')

    _sql_constraints = [
        ('date_prévue_check', "CHECK ( (date_depart_prevue <= date_retour_prevue))", "La date de départ prévue doit être inférieur à la date de retour prévue.")
    ]

    @api.depends('vehicle_id')
    def _get_vehicule_detail(self):
        for fr in self:
            if fr.vehicle_id:
                fr.marque_vehicle = fr.vehicle_id.model_id.name

    @api.onchange('vehicle_id')
    def get_info_vehicle(self):
        if not self.vehicle_id:
            return False

        else:
            voiture = self.vehicle_id

            self.conducteur_id = voiture.conducteur_id.id
            self.name = "FR"+self.vehicle_id.id+"2017"

    @api.onchange('frais_de_mission_ids')
    def set_state_to_confirmed(self):
        if self.frais_de_mission_ids:
            self.write({'state': 'confirmed'})

    @api.multi
    def create_frais_mission(self):
        res = self.env['ir.actions.act_window'].for_xml_id('wso_flotte_logistique', 'wso_flotte_frais_mission_action')
        res['domain'] = [('feuille_de_route_id','=', self.id)]
        res['context'] = {'default_res_model': 'wso_flotte_logistique', 'default_feuille_de_route_id': self.id}
        return res

    @api.multi
    def show_frais_mission(self):
        res = self.env['ir.actions.act_window'].for_xml_id('wso_flotte_logistique', 'wso_flotte_frais_mission_tree_action')
        res['domain'] = [('feuille_de_route_id','=', self.id)]
        res['context'] = {'default_res_model': 'wso_flotte_logistique', 'default_feuille_de_route_id': self.id}
        return res

    @api.multi
    def create_fiche_carburant(self):
        res = self.env['ir.actions.act_window'].for_xml_id('wso_flotte_logistique', 'fuel_vehicle_gestion_action')
        res['domain'] = [('feuille_de_route_id','=', self.id)]
        res['context'] = {'default_res_model': 'wso_flotte_logistique', 'default_feuille_de_route_id': self.id}
        return res

    @api.multi
    def show_fiche_carburant(self):
        res = self.env['ir.actions.act_window'].for_xml_id('wso_flotte_logistique', 'fuel_vehicle_gestion_action_tree')
        return res

    @api.multi
    def action_map_route(self):
        self.ensure_one()
        if not self.commande_ids:
            raise exceptions.Warning(_(
                'No order yet'))
        user_id = self.commande_ids[0].client_id.env.user.partner_id
        if not all([user_id.partner_longitude, user_id.partner_latitude]):
            raise exceptions.Warning(_(
                'You have not defined the admin geolocation'))
        context = self.env.context.copy()
        partner_origin_temp = user_id;
        i=0
        num = ''
        partners = []
        # For displaying map route for all orders from Origin (admin) to each client, iteratly
        for com in self.commande_ids:
            num = str(i)
            context.update({
                'origin_latitude'+num: partner_origin_temp.partner_latitude,
                'origin_longitude'+num: partner_origin_temp.partner_longitude,
                'destination_latitude'+num: com.client_id.partner_latitude,
                'destination_longitude'+num: com.client_id.partner_longitude,
                'total_count': i+1
            })
            partners.append(partner_origin_temp.id)
            partners.append(com.id)
            # the client become the origin to another client
            partner_origin_temp = com.client_id
            i+=1
            num = str(i)
#       Retour vers l'origine
        context.update({
                'default_partner_id':self.id,
                'origin_latitude'+num: partner_origin_temp.partner_latitude,
                'origin_longitude'+num: partner_origin_temp.partner_longitude,
                'destination_latitude'+num: user_id.partner_latitude,
                'destination_longitude'+num: user_id.partner_longitude,
                'show_orders': True
            })
        view_map_id = self.env.ref('web_google_maps.view_partner_map')
        return {
            'name': _('Map'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'map',
            'view_type': 'map',
            'views': [(view_map_id.id, 'map')],
            'context': context,
            'domain': [('id', 'in', partners)]
        }

    @api.model
    def set_total_distance(self, value, id):
        if not id:
            raise exceptions.Warning(_(
                'Feuille de route introuvable introuvable.'))
        partner_id = self.env['wso.flotte.route'].browse(id)
        if isinstance(value, float):
            partner_id.total_distance = value
            return partner_id.id
        else:
            return False

    @api.onchange('total_distance')
    def _compute_estimation_litre(self):
        vehicle = self.vehicle_id
        total = self.total_distance
        if(self.marge_km) : total = self.marge_km + self.total_distance
        if(vehicle.consommation):
            self.estimation_litre = (total*vehicle.consommation)/100

    @api.multi
    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('sale', 'email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "sale.mail_template_data_notification_email_sale_order"
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.onchange('responsable_zone','commercial','mobile_1','mobile_2')
    def _responsable_zone(self):
        self.passager = 0
        if self.responsable_zone:
            self.passager += 1
        if self.commercial:
            self.passager += 1
        if self.mobile_1:
            self.passager += 1
        if self.mobile_2:
            self.passager += 1

wso_flotte_route()

class wso_destination(models.Model):
    _name = "wso.flotte.destination"
    _description = "Destination de livraison"
    name = fields.Char(string='Nom de la ville', size=128)
    bareme_ration = fields.Float(string='Barème de ration (max)')

    _sql_constraints = [('wso_flotte_destination_name_unique','unique(name)', 'Le nom de ville �xiste d�j�')]

wso_destination()