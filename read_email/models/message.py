'''
Created on août 2017

@author: Antsa
'''
import email, imaplib ,re, os

class Message(object):
    ''' Classe contenant tous les messages d'un mail

    Attributes:
        category: sent/inbox/draft/...
        seen: True/False
        attached_files: liste fichiers attachés
        content: contenu
    '''


    def __init__(self, content, config):
        self.category = "INBOX"
        self.seen = True
        self.attached_files = False
        self.config = config
        self.content = content

    @property
    def content(self):
        return self.content

    @content.setter
    def content(self, value):
        mail = email.message_from_string(value) # parsing the mail content to get a mail object#        #Check if any attachments at all
        if mail.get_content_maintype() != 'multipart':
            continue
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
            self.attached_files = os.path.join(self.config.place_dos , filename)

            #Check if its already there
            if not os.path.isfile(self.attached_files) :
                # finally write the stuff
                fp = open(self.attached_files, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()

        self.content = mail