'''
Created on août 2017

@author: Antsa
'''
import message
import email, imaplib ,re

class Mail(object):
    ''' Classe représentant le mail d'une adresse, avec toutes les infos qui vont avec

    Attributes
        host: Le serveur de l'email (ex: Localhost, gmail, yahoo,...)
        address: adresse email
        password: mot de passe
        liste_message: liste de tous les messages
    '''


    def __init__(self, host, address, password):
        self.host = host
        self.address = address
        self.password = password

    def login(self):
        M = imaplib.IMAP4_SSL(self.host)
        M.login(self.address,self.password)
        return M

    def get_attached_files(self):
        M = self.login()
        M.select()
        data = M.search(None, '(UNSEEN)')
        for num in data[0].split():
            data = M.fetch(num, '(RFC822)')
            # get the content -> get attached files -> place them to local dir 'place_dos' (cf. your configuration file)
            message.Message(data[0][1])
            M.store(num, '+FLAGS', '(\Deleted)')
        M.close()
        M.logout()
