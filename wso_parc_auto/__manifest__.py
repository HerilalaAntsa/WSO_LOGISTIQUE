# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) Dzama Consulting (ajoharym@gmail.com).
#
##############################################################################

{
    'name': 'WISO-wso_parc_auto-Flotte Extended Module',
    'version': '1.0',
    'category': 'fleet',
    'description': """ Module specifique pour les besoins dans parc automobile,  """,
    'author': 'Dzama Consulting (ajoharym@gmail.com)',
    'website': 'http://www.dzama.mg',
    'license': 'AGPL-3',
    'depends': ['fleet', 'project', 'account', 'sale', 'hr'],

    'init_xml': [],

    'demo_xml': [],
    'data': [
        'security\ir.model.access.csv',
        'vehicle_view.xml',#add by Johary--------------------------
        'wso_parkauto_model.xml',


    ],
    'active': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: