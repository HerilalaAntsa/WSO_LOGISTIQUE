# -*- coding: utf-8 -*-

{
    'name': 'wso_fuel_gestion - GESTION CARBURANT SIMPLIFIEE',
    'version': '1.0',
    'category': 'account',
    'description': """ Module specifique pour la gestion du carburant """,
    'author': 'Dzama Consulting (ajoharym@gmail.com)',
    'website': 'http://www.dzama.mg',
    'license': 'AGPL-3',
    'depends': [
                'fleet', 'base'
                ],

    'update_xml':[
                  'security/ir.model.access.csv',
                  'security/fuel_access.xml',
                  'fiche_carburant.xml',
                  'wizard/import_fuel.xml',

                  ],
    'data':[
            ],
    'demo_xml': [],
    'active': False,
    'installable': True,
}

