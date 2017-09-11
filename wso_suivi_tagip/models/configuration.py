# -*- coding: utf-8 -*-
'''
Created on ao�t 2017

@author: Antsa
'''
from odoo import models, fields, api, _
import email, imaplib ,re, os, time, zipfile, sys
from odoo.exceptions import UserError
import email, imaplib
import ConfigParser
import logging
_logger = logging.getLogger(__name__)
d = os.path.dirname(__file__)

cfg = ConfigParser.ConfigParser()
filename = os.path.join(d , 'configuration.cfg')
cfg.read(filename)
db_name_cfg = cfg.get('Connex', 'db_name')
db_user_cfg = cfg.get('Connex', 'db_user')
db_pass_cfg = cfg.get('Connex', 'db_pass')
db_port_cfg = cfg.get('Connex', 'db_port')
db_host_cfg = cfg.get('Connex', 'db_host')

place_dos_cfg = cfg.get('Connex', 'place_dos')
place_unzip_cfg = cfg.get('Connex', 'place_unzip')

mail_user_cfg = cfg.get('Connex', 'mail_user')
mail_pass_cfg = cfg.get('Connex', 'mail_pass')
mail_host_cfg = cfg.get('Connex', 'mail_host')

auto_tagip_report_up = cfg.get('Connex', 'auto_download')

db_user = cfg.get('Connex', 'db_user')
db_pass = cfg.get('Connex', 'db_pass')
db_port = cfg.get('Connex', 'db_port')
db_host = cfg.get('Connex', 'db_host')

class Configuration(models.TransientModel):
    _name = "wso.tagip.config"
    _inherit = 'res.config.settings'
    _description = "Connection to an email to see all messages and get all attached files."

    db_name = fields.Char(string='Nom de la base de donn�e', default=db_name_cfg)
    db_user = fields.Char(string='Nom de l\'utilisateur (BDD)', default=db_user_cfg)
    db_pass = fields.Char(string='Mot de passe (BDD)')
    db_port = fields.Char(string='Port (BDD)', default='5432')
    db_host = fields.Char(string='Host (BDD)', default='localhost')
    place_dos = fields.Char(string='Chemin pour placer les fichiers .ZIP', default=place_dos_cfg)
    place_unzip = fields.Char(string='Chemin pour placer les fichiers téléchargés', default='REPORTS')
    mail_user = fields.Char(string='Adresse email', default=mail_user_cfg)
    mail_pass = fields.Char(string='Mot de passe email')
    mail_host = fields.Char(string='Serveur de Mail', default='ssl0.ovh.net')

    report_cat = fields.Char(string='Categorie du rapport', default='RPT.SYS.DET.24', readonly=True)
    frequence = fields.Char(string='Frequence', default='24', readonly=True)
    flotte_type = fields.Selection([
                                        ('DZA.LIV.TNA', 'Livraison'),
                                        ('DZA.MOTO.TNA', 'Moto'),
                                        ('DZA.SUV.TNA', 'SUV'),
                                        ('TOUS', 'TOUS')
                                    ],
                                    default='DZA.LIV.TNA',
                                    string='Categorie de flotte',
                                    help= "Selectionner le type de flotte")

    auto_tagip_report_up = fields.Boolean(
        string='Automatic TAGIP Reports Download', default=False,
        help="Automatic download all new attachement files about reports from TAGIP's mail")

    @api.multi
    def generate_configuration(self):
        cfg = ConfigParser.ConfigParser()
        S = 'Connex'
        cfg.add_section(S)
        cfg.set(S, 'mail_user', self.mail_user)
        cfg.set(S, 'mail_pass', self.mail_pass)
        cfg.set(S, 'mail_host', self.mail_host)

        cfg.set(S, 'place_dos', self.place_dos)
        cfg.set(S, 'place_unzip', self.place_unzip)

        cfg.set(S, 'db_name', self.db_name)
        cfg.set(S, 'db_user', self.db_user)
        cfg.set(S, 'db_pass', self.db_pass)
        cfg.set(S, 'db_port', self.db_port)
        cfg.set(S, 'db_host', self.db_host)

        cfg.set(S, 'auto_download', self.auto_tagip_report_up)

        cfg.set(S, 'report_cat', self.report_cat)
        cfg.set(S, 'date', self.date)
        cfg.set(S, 'frequence', self.frequence)
        cfg.set(S, 'flotte_type', self.flotte_type)

        with open(os.path.join(d , 'configuration.cfg'), 'w') as configfile:
            cfg.write(configfile)

#         vals = {
#             'mail_user': self.mail_user,
#             'mail_pass': self.mail_pass,
#             'mail_host': self.mail_host,
#             'place_dos': self.place_dos,
#             'place_unzip': self.place_unzip,
#             'db_name': self.db_name,
#             'db_user': self.db_user,
#             'db_pass': self.db_pass,
#             'db_port': self.db_port,
#             'db_host': self.db_host,
#         }
#         self.create(vals)

    @api.onchange('auto_tagip_report_up')
    def is_auto_download_report(self):
        if not(self.db_name and self.db_user and self.db_pass and self.db_port and
            self.db_host and self.place_unzip and
                self.mail_user and self.mail_pass and self.mail_host):
            self.auto_tagip_report_up = not self.auto_tagip_report_up
            raise UserError(_("Veuillez remplir tous les champs !"))
