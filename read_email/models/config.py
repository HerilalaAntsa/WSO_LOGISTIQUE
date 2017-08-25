'''
Created on août 2017

@author: Antsa
'''
import ConfigParser
from __builtin__ import file

class ConfigConnex(object):
    user = 'tagip@dzama.mg'
    password = 'bottagip2015'
    place_dos = 'data'
    place_zip = 'data/DZA'
    db_name = 'odoo_test'
    user_base = 'odoo9pg'
    pass_bases = 'odoo9pgpwd'
    port = '5432'
    host = 'localhost'


    def __init__(self, user,password,place_dos,place_zip,db_name,user_base,pass_bases,port,host):
        self.user = user
        self.password = password
        self.place_dos = place_dos
        self.place_zip = place_zip
        self.db_name = db_name
        self.user_base = user_base
        self.pass_bases = pass_bases
        self.port = port
        self.host = host

    def read_config(self, file):
        cfg = ConfigParser.ConfigParser()
        if not file:
            file = 'configuration.cfg'

        cfg.read(file)
        db_name=cfg.get('Connex', 'db_name')
        user_base = cfg.get('Connex', 'user_base')
        password=cfg.get('Connex', 'pass_bases')
        place_fich=cfg.get('Connex', 'place_dos')
        place_zip=cfg.get('Connex', 'place_zip')
        user_tag=cfg.get('Connex', 'user')
        pass_tag=cfg.get('Connex', 'password')
        port=cfg.get('Connex', 'port')
        host=cfg.get('Connex', 'host')

class ConfigCarburant(object):
    place_dossier = 'releve_kilometrique/data'
    mail_carb = 'flotte@dzama.mg'
    pass_carb = 'bot2015flot'


    def __init__(self, place_dossier,mail_carb,pass_carb):
        self.place_dossier = place_dossier
        self.mail_carb = mail_carb
        self.pass_carb = pass_carb