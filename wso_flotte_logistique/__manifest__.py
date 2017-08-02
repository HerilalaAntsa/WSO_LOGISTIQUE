# -*- coding: utf-8 -*-
{
    'name': 'Logistique de la compagnie vidzar',
    'version': '1.0',
    'category': 'Distribution',
    'description': """Module comprenant le suivi de la flotte automobile : suivi carburant, itineraires vehicules..""",
    'author': 'Dzama Consulting (herilala.antsa@gmail.com)',
    'website': 'http://www.dzama.mg',
    'license': 'AGPL-3',
    'depends': ['wso_parc_auto','web_google_maps'],
    'init_xml': [],
    'demo_xml': [],
    'data': [
#                 'security\ir.model.access.csv',
                'views/feuille_de_route.xml',
                'views/wso_arret.xml',
#                 'views\wso_trajet.xml',
#                 'views/distrib_lieu.xml'
#                 'views\mouv.xml',
                'views/frais_de_mission.xml'
            ],
    'active': False,
    'installable': True,
}