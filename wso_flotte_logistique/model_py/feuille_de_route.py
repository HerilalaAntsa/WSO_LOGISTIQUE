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
from odoo import  fields, models, api
import datetime
from odoo import tools
from odoo.tools.translate import _


def str_to_datetime(strdate):
    return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)


class wso_flotte_route(models.Model):
    _name = "wso.flotte.route"
    _description = "Ordre de mission pour la livraison de la distribution Vidzar"

    name = fields.Text(string='Remarque sur le véhicule')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicule', required=True)
    conducteur_id = fields.Many2one('fleet.driver', string='Conducteur')    # set by a @OnChange('vehicule_id')

    responsable_zone = fields.Char('Responsable zone', size=128)
    commercial = fields.Char('Commercial', size=128)
    mobile_1 = fields.Char('Mobile 1', size=128)
    mobile_2 = fields.Char('Mobile 2', size=128)
    facture = fields.Char('N° Facture', size=128)

    date_saisie = fields.Date('Date de saisie', size=128)
    date_depart_prevue = fields.Date('Date de départ prévu', size=128)
    date_retour_prevue = fields.Date('Date de retour prévu', size=128)
    date_depart = fields.Date('Date de départ', size=128)
    date_retour = fields.Date('Date de retour', size=128)

    destination_id = fields.Many2one('wso.flotte.destination', string='Destination', required=True)
    passager = fields.Integer('Nombre de passagers')
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
    # Une feuille de route ne pourra avoir qu'un seul frais de mission (aucun doublon)
    frais_de_mission_ids = fields.One2many('wso.flotte.frais.mission', 'feuille_de_route_id', string='Frais de mission')

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
            observation = voiture.observation

            self.conducteur_id = voiture.conducteur_id.id
            self.name = observation

    @api.multi
    def create_frais_mission(self):
        form_id = self.env.ref('wso_flotte_logistique.view_frais_mission_form').id
        tree_id = self.env.ref('wso_flotte_logistique.view_frais_mission_tree').id
        context =  {'default_invoice_id': self.id, 'default_res_id': self.id}
        return {
            'name':'creer_frais_de_mission',
            'view_type':'form',
            'view_mode':'form',
            'views' : [(form_id,'form')],
            'res_model':'wso.flotte.frais.mission',
            'view_id':form_id,
            'type':'ir.actions.act_window',
            'res_id':self.id,
            'target':'current',
            'context':context,
        }

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

wso_flotte_route()

class wso_destination(models.Model):
    _name = "wso.flotte.destination"
    _description = "Destination de livraison"
    name = fields.Char(string='Nom de la ville', size=128)
    bareme_ration = fields.Float(string='Barème de ration (max)')

    _sql_constraints = [('wso_flotte_destination_name_unique','unique(name)', 'Le nom de ville �xiste d�j�')]

wso_destination()