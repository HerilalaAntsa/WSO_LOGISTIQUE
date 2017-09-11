# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) Dzama Consulting (ajoharym@gmail.com).
#
##############################################################################

{
    'name': 'WISO - TAGIP Reports Download Module',
    'version': '1.0',
    'category': 'fleet',
    'description': """ Module specifique pour le telechargement des comptes rendus journaliers venant de TAGIP via mail.  """,
    'author': 'Dzama Consulting (herilala.antsa@gmail.com)',
    'website': 'http://www.dzama.mg',
    'license': 'AGPL-3',
    'depends': ['wso_flotte_logistique'],

    'init_xml': [],

    'demo_xml': [],
    'data': [
        'views/configuration.xml',
        'views/report.xml',
        'data/cron.xml',
    ],
    'active': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: