# -*- coding: utf-8 -*-
{
    'name': 'Logistique de la compagnie vidzar',
    'version': '1.0',
    'category': 'Distribution',
    'description': """Module comprenant le suivi de la flotte automobile : suivi carburant, itineraires vehicules..""",
    'author': 'Dzama Consulting (herilala.antsa@gmail.com)',
    'website': 'http://www.dzama.mg',
    'license': 'AGPL-3',
    'depends': ['wso_parc_auto','web_google_maps','wso_fuel_gestion'],
    'init_xml': [],
    'demo_xml': [],
    'data': [
#                 'security\ir.model.access.csv',
                'views/google_places_template.xml',
                'views/sequence.xml',
                'views/feuille_de_route.xml',
                'views/frais_de_mission.xml',
# #                 'views/wso_arret.xml',
# #                 'views\wso_trajet.xml',
# #                 'views/distrib_lieu.xml'
# #                 'views\mouv.xml',
                'views/fleet_view.xml',
                'views/res_partner_view.xml',
                'views/fiche_carburant.xml'
            ],
#     'qweb': ['static/src/xml/widget_places.xml'],
    'active': False,
    'installable': True,
}