# -*- coding: utf-8 -*-
'''
Created on ao�t 2017

@author: Antsa
'''
from odoo import models, fields, api
import email, imaplib ,re, os, time, zipfile, sys
import ConfigParser
from odoo.exceptions import UserError
import email, imaplib
import xlrd
import unidecode
from datetime import datetime , timedelta
import logging
_logger = logging.getLogger(__name__)
d = os.path.dirname(__file__)
data_path = os.path.join(os.path.dirname(d), 'data')

db_name = ''
db_user = ''
db_pass = ''
db_port = ''
db_host = ''
place_dos = ''
place_unzip = ''
mail_user = ''
mail_pass = ''
mail_host = ''
report_cat = ''
date = ''
frequence = ''
flotte_type = ''
auto_tagip_report_up = ''

# numero de colonne Excel (Résumé mouvement):
VEHICULE = 0
IMMATRICULATION = 1
DATEDEBUT = 2
DATEFIN = 3
DUREEROULAGE = 4
DISTANCEPARCOURUE = 5
VITESSEMOYENNE = 6
VITESSEMAXIMUM = 7
DUREEARRET = 8
NOMBREARRET = 9

class DownloadReports(models.Model):
    _name = "wso.tagip.download.reports"

    def set_config(self):
        global db_name, db_user, db_pass, db_port, db_host, place_dos, place_unzip, mail_user, mail_pass, mail_host, auto_tagip_report_up
        global report_cat, date, frequence, flotte_type
        cfg = ConfigParser.ConfigParser()
        filename = os.path.join(d , 'configuration.cfg')
        if(cfg.read(filename)):
            db_name = cfg.get('Connex', 'db_name')
            db_user = cfg.get('Connex', 'db_user')
            db_pass = cfg.get('Connex', 'db_pass')
            db_port = cfg.get('Connex', 'db_port')
            db_host = cfg.get('Connex', 'db_host')

            place_dos = cfg.get('Connex', 'place_dos')
            place_unzip = cfg.get('Connex', 'place_unzip')

            mail_user = cfg.get('Connex', 'mail_user')
            mail_pass = cfg.get('Connex', 'mail_pass')
            mail_host = cfg.get('Connex', 'mail_host')

            report_cat = cfg.get('Connex', 'report_cat')
            frequence = cfg.get('Connex', 'frequence')
            flotte_type = cfg.get('Connex', 'flotte_type')

            auto_tagip_report_up = cfg.get('Connex', 'auto_download')
        else:
            raise UserError(_("Veuillez enregistrer une configuration!"))

    @api.multi
    def login(self):
        global db_name, db_user, db_pass, db_port, db_host, place_dos, place_unzip, mail_user, mail_pass, mail_host, auto_tagip_report_up
        M = imaplib.IMAP4_SSL(mail_host)
        M.login(mail_user,mail_pass)
        return M

    def get_mail_content(self, value):
        global db_name, db_user, db_pass, db_port, db_host, place_dos, place_unzip, mail_user, mail_pass, mail_host, auto_tagip_report_up
        global report_cat, date, frequence, flotte_type
        files = list()
        mail = email.message_from_string(value) # parsing the mail content to get a mail object
#         # Check only for TAGIP reports
#         print mail['subject']
#         if not re.search(r'\bCompteb', mail['subject']):
#             return False
        #Check if any attachments at all
        if mail.get_content_maintype() != 'multipart':
            return False
        # we use walk to create a generator so we can iterate on the parts and forget about the recursive headache
        for part in mail.walk():
            # multipart are just containers, so we skip them
            if part.get_content_maintype() == 'multipart':
                continue
            counter = 1
            # is this part an attachment ?
            if part.get('Content-Disposition') is None:
                continue
            filename = part.get_filename()
            counter += 1
            # if there is no filename, we create one with a counter to avoid duplicates
            if not filename:
                filename = 'part-%03d%s' % (counter, 'bin')
                counter += 1

            attached_files = os.path.join(os.path.join(data_path, place_unzip) , filename)

            # Sort files according to configuration file
            # Download only what we need
            tab = re.match(r'(.+)-([0-9]+)-(.+)-(.+).xlsx', filename, re.M|re.I)
            r_c = tab.group(1)
            date = datetime.strptime(tab.group(2), '%Y%m%d').strftime('%Y-%m-%d')
            freq = tab.group(3)
            f_t = tab.group(4)
            if not r_c == report_cat:
                continue
            if not freq == frequence:
                continue
            if not flotte_type == 'TOUS':
                if not f_t == flotte_type:
                    continue

            #Check if its already there
            if not os.path.isfile(attached_files) :
                # finally write the stuff
                fp = open(attached_files, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()

            files.append(attached_files)
        return files

    @api.multi
    def get_attached_files(self):
        files = list()
        M = self.login()
        M.select('INBOX')
        type, data = M.search(None, '(UNSEEN)')
        for num in data[0].split():
            type, data = M.fetch(num, '(RFC822)')
            # get the content -> get attached files -> place them to local dir 'place_unzip' (cf. your configuration file)
            attached_files = self.get_mail_content(data[0][1])
            files.extend(attached_files)
            #Mark the email as SEEN or DELETED
            M.store(num, '+FLAGS', '(\SEEN)')
        M.close()
        M.logout()
        return files

    @api.multi
    def dezip(self, filezip):
        pathdst = place_unzip + time.strftime('%d-%m-%Y')
        print filezip
        print pathdst
        if pathdst == place_dos: pathdst = os.getcwd()  ## on dezippe dans le repertoire locale
        zfile = zipfile.ZipFile(filezip, 'r')
        for i in zfile.namelist():  ## On parcourt l'ensemble des fichiers de l'archive

            if os.path.isdir(i):   ## S'il s'agit d'un repertoire, on se contente de creer le dossier
                try: os.makedirs(pathdst + os.sep + i)
                except: pass
            else:
                try: os.makedirs(pathdst + os.sep + os.path.dirname(i))
                except: pass
                datav = zfile.read(i)                   ## lecture du fichier compresse
                fp = open(pathdst + os.sep + i, "wb")   ## creation en local du nouveau fichier
                fp.write(datav)                         ## ajout des donnees du fichier compresse dans le fichier local
                fp.close()
        zfile.close()
        return pathdst

    def search_for_header(self, worksheet):
        index = 0;
        while index < 20:
            tab = []
            for v in worksheet.row(index):
                if v.value != '':
                    tab.append(v)
            if len(tab) <= 5:
                index += 1
            else: return index
        return -1

    def parse_xls_resume_to_object(self, workbook, sheet_index):
        worksheet = workbook.sheet_by_index(sheet_index)

        data = []
        keys = []
        header_ind = self.search_for_header(worksheet)
        if header_ind >= 0:
            keys = [unidecode.unidecode(v.value.lower()) for v in worksheet.row(header_ind)]
        else:
            raise Exception('Impossible de lire le fichier Excel.')

        try:
            for row_number in range(worksheet.nrows):
                if row_number <= header_ind:
                    continue
                row_data = {}
                for col_number, cell in enumerate(worksheet.row(row_number)):
                    # To know if a vahicle has a report or not
                    if worksheet.cell(rowx = row_number , colx =2 ).value == '':
                        continue
                    # If date
                    if col_number == DATEDEBUT or col_number == DATEFIN:
                        heures = xlrd.xldate.xldate_as_datetime(cell.value,workbook.datemode)
                        heure=heures.strftime('%H:%M:%S')
                        dateu = xlrd.xldate.xldate_as_datetime(cell.value,workbook.datemode)
                        date = dateu.strftime('%d-%m-%Y')
                        row_data[keys[col_number]] = date +' '+heure
                    # If duree
                    elif col_number == DUREEROULAGE or col_number == DUREEARRET:
                        heures = xlrd.xldate.xldate_as_datetime(cell.value,workbook.datemode) + timedelta(days=1)
                        heure=heures.strftime('%H:%M:%S')
                        row_data[keys[col_number]] = heure
                    # If text
                    else:
                        if isinstance(cell.value, float):
                            row_data[keys[col_number]] = "%.2f" % cell.value
                        else: row_data[keys[col_number]] = cell.value
                if row_data:
                    data.append(row_data)
            return data
        except Exception as e:
            raise Exception(('Error while parsing Excel file. \n Details: '+ str(e)))


    @api.multi
    def read_xls(self):
        global db_name, db_user, db_pass, db_port, db_host, place_dos, place_unzip, mail_user, mail_pass, mail_host, auto_tagip_report_up
        global report_cat, date, frequence, flotte_type
        path = os.path.join(data_path, place_unzip)
        doc = [f for f in os.listdir(path) if f.endswith('.xlsx')]
        # loop file
        for f  in doc :
            res=path + '/'+f
            workbook = xlrd.open_workbook( )
            # loop sheets
            for sheet in workbook.sheets():
                if unidecode.unidecode(sheet.name) == 'Resume':
                    data = self.parse_xls_resume_to_object(workbook, 0)
                    report = [ResumeReport(resume) for resume in data]
                    for rep in report:
                        print rep
                        id_report = None
                        wso_report = self.env["wso.tagip.report"]
                        repo = wso_report.search([("date", "=", str(date))])
                        if repo:
                            for r in repo:
                                id_report = r.id
                        else:
                            id_report = wso_report.create({
                                    'name': str(date),
                                    'frequence': frequence,
                                    'flotte_type': flotte_type,
                                    'date': str(date),
                                    'work_for': flotte_type,
                                })
                            print 'id_report '+ id_report

                elif unidecode.unidecode(sheet.name) == 'Evenement':
                    continue
                else:
                    continue
#                 if 'nement' in sheet.name:
#                     print 'liste des évenements'


    @api.multi
    def run_currency_tagip(self):
        global db_name, db_user, db_pass, db_port, db_host, place_dos, place_unzip, mail_user, mail_pass, mail_host, auto_tagip_report_up
        global report_cat, date, frequence, flotte_type
        self.set_config()
        _logger.info(
            'Starting to download TAGIP reports from the address %s ',
            mail_user)
        if(auto_tagip_report_up):
            try:
                attached_files = self.get_attached_files()
                self.read_xls()
#                 des_unzip = self.dezip(attached_files)
#                 os.remove(attached_files)
            except Exception as exc:
                    _logger.error(repr(exc))

    @api.multi
    def _run_currency_tagip(self):
        self.run_currency_tagip()
        _logger.info('End of the TAGIP reports download cron')

class ResumeReport:
    def __init__(self, data):
        self.data = data

    def getVehicule(self):
        return self.data["vehicule"]

    def getImmatriculation(self):
        return self.data["immatriculation"]

    def getDateDebut(self):
        return self.data["date de debut"]

    def getDateFin(self):
        return self.data["date de fin"]

    def getDureeRoulage(self):
        return self.data["duree de roulage"]

    def getDistanceParcourue(self):
        return self.data["distance parcourue"]

    def getVitesseMoyenne(self):
        return self.data["vitesse moyenne"]

    def getVitesseMaximum(self):
        return self.data["vitesse maximale"]

    def getDureeArret(self):
        return self.data["duree des arrets"]

    def getNombreArret(self):
        return self.data["nombre d'arrets"]
