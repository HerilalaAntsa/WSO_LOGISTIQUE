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
import logging
_logger = logging.getLogger(__name__)
d = os.path.dirname(__file__)

class DownloadReports(models.Model):
    _name = "wso.tagip.download.reports"

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
    auto_tagip_report_up = ''

    def set_config(self):
        print 'db_name ' + self.db_name
        cfg = ConfigParser.ConfigParser()
        filename = os.path.join(d , 'configuration.cfg')
        if(cfg.read(filename)):
            self.db_name = cfg.get('Connex', 'db_name')
            self.db_user = cfg.get('Connex', 'db_user')
            self.db_pass = cfg.get('Connex', 'db_pass')
            self.db_port = cfg.get('Connex', 'db_port')
            self.db_host = cfg.get('Connex', 'db_host')

            self.place_dos = cfg.get('Connex', 'place_dos')
            self.place_unzip = cfg.get('Connex', 'place_unzip')

            self.mail_user = cfg.get('Connex', 'mail_user')
            self.mail_pass = cfg.get('Connex', 'mail_pass')
            self.mail_host = cfg.get('Connex', 'mail_host')

            auto_tagip_report_up = cfg.get('Connex', 'auto_download')
            print self.db_name
        else:
            raise UserError(_("Veuillez enregistrer une configuration!"))

    @api.multi
    def login(self):
        M = imaplib.IMAP4_SSL(self.mail_host)
        M.login(self.mail_user,self.mail_pass)
        return M

    def get_mail_content(self, value):
        files = list()
        mail = email.message_from_string(value) # parsing the mail content to get a mail object
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

            attached_files = os.path.join(self.place_unzip , filename)

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
        self.set_config()
        files = list()
        M = self.login()
        M.select('INBOX')
        data = M.search(None, '(UNSEEN)')
        for num in data[0].split():
            data = M.fetch(num, '(RFC822)')
            print data
            # get the content -> get attached files -> place them to local dir 'place_unzip' (cf. your configuration file)
            attached_files = self.get_mail_content(data[0][1])
            files.append(f for f in attached_files)
            #Mark the email as SEEN or DELETED
            M.store(num, '+FLAGS', '(\SEEN)')
        M.close()
        M.logout()
        return files

    @api.multi
    def dezip(self, filezip):
        pathdst = self.place_unzip + time.strftime('%d-%m-%Y')
        print filezip
        print pathdst
        if pathdst == self.place_dos: pathdst = os.getcwd()  ## on dezippe dans le repertoire locale
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

    @api.multi
    def run_currency_tagip(self):

        _logger.info(
            'Starting to download TAGIP reports from the address %s ',
            self.mail_user)
        if(self.auto_tagip_report_up):
            try:
                attached_files = self.get_attached_files()
                print attached_files
#                 des_unzip = self.dezip(attached_files)
#                 os.remove(attached_files)
            except Exception as exc:
                    _logger.error(repr(exc))

    @api.multi
    def _run_currency_tagip(self):
        self.run_currency_tagip()
        _logger.info('End of the TAGIP reports download cron')