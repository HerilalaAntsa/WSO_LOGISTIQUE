# -*- coding: utf-8 -*-


from openerp.osv import fields, osv
import time
import datetime
from openerp import tools
from openerp.osv.orm import except_orm
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
def str_to_datetime(strdate):
    return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)

class wso_fiche_control (osv.osv):
    _name = "wso.fleet.control"
    _description = "Control des vehicules"

    _columns = {
        'vec_id': fields.many2one('fleet.vehicle','Vehicule'),
        'date_cont':fields.datetime(string='Date du controle', size=128),
        'chauffeur': fields.char(string='Conducteur lié', size=128),
        'notes': fields.text(string='Causes et remarque liée :'),
        'degat':fields.binary(string= 'Image de constataion'),
        'agent': fields.char(string='Agent controleur :'),
        'etat_caross':fields.char(string='Etat:', size = 50),
        'note_caross':fields.text(string='Description:' ,size =90),
        'etat_equip':fields.char(string='Etat:', size = 50 ),
        'note_equip':fields.text(string='Description:' ,size =90),
        'etat_moteur':fields.char(string='Etat:', size = 50 ),
        'note_moteur':fields.text(string='Description:' ,size =90),
        'etat_pneu':fields.char(string='Etat:', size = 50 ),
        'note_pneu':fields.text(string='Description:' ,size =90),
        'etat_frein':fields.char(string='Etat:', size = 50 ),
        'note_frein':fields.text(string='Description:' ,size =90),
        'photo':fields.binary(string='Etat actuel',size = 50 ),
        'level_fuel' : fields.float('Niveau Carburant'),
        'distance_km' : fields.float('Kilometrage')
                }

wso_fiche_control()
class wso_fleet_fich (osv.osv):
    _inherit = "fleet.vehicle"
    _description = "Control fiches des vehicules"
    _columns = {
        'fiche_ids': fields.one2many('wso.fleet.control','vec_id'),
                }