'''
Created on 16 août 2017

@author: kiboy
'''
import os, zipfile, sys
import xlrd

class Utilitaire(object):


    def __init__(self, params):
        '''
        Constructor
        '''

    @staticmethod
    def dezip_files(filezip, path_dest = ''):
#         # dezip in the local dir
#         if path_dest == place_fich:
#             path_dest = os.getcwd()
        zfile = zipfile.ZipFile(filezip, 'r')
        for i in zfile.namelist():  ## On parcourt l'ensemble des fichiers de l'archive
            # if it is a dir, we create the folder
            if os.path.isdir(i):
                try: os.makedirs(path_dest + os.sep + i)
                except: pass
            else:
                try: os.makedirs(path_dest + os.sep + os.path.dirname(i))
                except: pass
                datav = zfile.read(i)
                fp = open(path_dest + os.sep + i, "wb")
                fp.write(datav)
                fp.close()
                zfile.close()

    @staticmethod
    def read_xml(file, path = ''):
        if not file.endswith('.xlsx'):
            raise ValueError('The file need to have .xlsx as extention.')
        res=path + '/'+file
        book = xlrd.open_workbook(res , sys.stdout.encoding)
