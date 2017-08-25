# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
# from tempfile import TemporaryFile
import odoo
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo import  models, api, fields
import tempfile

import xlrd
import unicodedata
from datetime import datetime

_logger = logging.getLogger(__name__)


COLUMN_SELECTION = []

class importFuel(models.Model):
    _name = 'import.fuel'
    _rec_name = 'name'


    import_data_fuel_id = fields.Many2one('import.data.fuel', string='import_id', store=True)
    name = fields.Char(string='Nom', related='import_data_fuel_id.name')
    model_import_id = fields.Many2one('import.fuel', string='Modele precedent')
    use_model = fields.Boolean(string='Use model')

    save_data = fields.Selection([('to_ignore','Non'), ('to_save', 'Oui')], string='state', default='to_ignore')


    #Colonnes necessaires pour la gestion de carburant
    fuel_vehicle_id = fields.Selection(COLUMN_SELECTION, string='Vehicule', copy=True)
    fuel_date = fields.Selection(COLUMN_SELECTION, string='Date', copy=True)
    fuel_beneficiaire = fields.Selection(COLUMN_SELECTION, string='Beneficiaire', copy=True)
    fuel_kilometrage = fields.Selection(COLUMN_SELECTION, string='Kilometrage', copy=True)
    fuel_amount = fields.Selection(COLUMN_SELECTION, string='Montant', copy=True)
    fuel_price_unit = fields.Selection(COLUMN_SELECTION, string='Prix unitaire', copy=True)
    fuel_qty = fields.Selection(COLUMN_SELECTION, string='Quantite', copy=True)
    fuel_hour = fields.Selection(COLUMN_SELECTION, string='Heure', copy=True)
    fuel_partner_id = fields.Selection(COLUMN_SELECTION, string='Societe', copy=True)
    fuel_libelle = fields.Selection(COLUMN_SELECTION, string='Libelle', copy=True)
    fuel_order_number = fields.Selection(COLUMN_SELECTION, string='BC', copy=True)
    fuel_invoice_number = fields.Selection(COLUMN_SELECTION, string='Facture', copy=True)
    fuel_panne = fields.Selection(COLUMN_SELECTION, string='Tableau km', copy=True)
    fuel_tagip = fields.Selection(COLUMN_SELECTION, string='TAG IP', copy=True)
    fuel_complement = fields.Selection(COLUMN_SELECTION, string='Complement', copy=True)



    @api.multi
    def get_column(self):
        #Reinitialisation des colonnes
        COLUMN_SELECTION[:] = []

        import_id = self.import_data_fuel_id
        if import_id:
            fuel_name = import_id.filename

            #Recuperation de l'emplacement du fichier
            #tempfile.gettempdir() recupere l'emplacement temporaire du fichier
            file_path = tempfile.gettempdir() +'//'+ fuel_name
            data = import_id.data
            f = open(file_path, 'wb')
            f.write(data.decode('base64'))
            f.close()

            #Ouverture du fichier
            book = xlrd.open_workbook(file_path)
            sheet = book.sheet_by_index(0)

            #Recuperation de la premiere ligne (nom de colonne)
            for col_index in xrange(sheet.ncols):
                row_index = 0
                name_column = sheet.cell(rowx=row_index, colx=col_index).value
                col_index = str(col_index)
                COLUMN_SELECTION.append((col_index, name_column)) #mise a jour valeur selection

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
         }



    @api.onchange('model_import_id')
    def onchange_column(self):
        model_data_import = self.model_import_id
        if model_data_import:
            self.fuel_vehicle_id = model_data_import.fuel_vehicle_id
            self.fuel_date = model_data_import.fuel_date
            self.fuel_beneficiaire = model_data_import.fuel_beneficiaire
            self.fuel_kilometrage = model_data_import.fuel_kilometrage
            self.fuel_amount = model_data_import.fuel_amount
            self.fuel_price_unit = model_data_import.fuel_price_unit
            self.fuel_qty = model_data_import.fuel_qty
            self.fuel_hour = model_data_import.fuel_hour
            self.fuel_partner_id = model_data_import.fuel_partner_id
            self.fuel_libelle = model_data_import.fuel_libelle
            self.fuel_order_number = model_data_import.fuel_order_number
            self.fuel_invoice_number = model_data_import.fuel_invoice_number
            self.fuel_panne = model_data_import.fuel_panne
            self.fuel_tagip = model_data_import.fuel_tagip
            self.fuel_complement = model_data_import.fuel_complement

    @api.onchange('use_model')
    def onchange_save_data(self):
        if self.use_model == True:
            self.save_data = 'to_ignore'



    @api.multi
    def wso_import_data(self):
        res = self.env['ir.actions.act_window'].for_xml_id('wso_fuel_gestion', 'fuel_vehicle_gestion_action')
        self.insert_fuel_value()


        return res



    @api.multi
    def unicode_transformation(self, to_transform):
        result = unicodedata.normalize('NFKD', to_transform).encode('ascii', 'ignore')
        return result

    @api.multi
    def insert_fuel_value(self):
        import_id = self.import_data_fuel_id

        fuel_vehicle_id = self.fuel_vehicle_id
        fuel_date = self.fuel_date
        fuel_beneficiaire = self.fuel_beneficiaire
        fuel_kilometrage = self.fuel_kilometrage
        fuel_amount = self.fuel_amount
        fuel_price_unit = self.fuel_price_unit
        fuel_qty = self.fuel_qty
        fuel_hour = self.fuel_hour
        fuel_partner_id = self.fuel_partner_id
        fuel_libelle = self.fuel_libelle
        fuel_order_number = self.fuel_order_number
        fuel_invoice_number = self.fuel_invoice_number
        fuel_panne = self.fuel_panne
        fuel_tagip = self.fuel_tagip
        fuel_complement = self.fuel_complement

        if import_id:
            fuel_name = import_id.filename

            #Recuperation de l'emplacement du fichier
            file_path = tempfile.gettempdir() +'//'+ fuel_name
            data = import_id.data
            f = open(file_path, 'wb')
            f.write(data.decode('base64'))
            f.close()

            #Ouverture du fichier
            book = xlrd.open_workbook(file_path)
            sheet = book.sheet_by_index(0)

            for row_index in xrange(sheet.nrows):

                if row_index > 0 :
                    libelle = sheet.cell(rowx=row_index,colx=int(fuel_libelle)).value
                    print "valeur libelle", libelle
                    if libelle:
                        libelle = self.unicode_transformation(libelle.upper())
                    if not libelle: libelle = ''

                    num_order = sheet.cell(rowx=row_index,colx=int(fuel_order_number)).value
                    if num_order:
                        num_order = self.unicode_transformation(num_order.upper())
                    if not num_order: num_order = ''

                    num_invoice = sheet.cell(rowx=row_index,colx=int(fuel_invoice_number)).value
#                     if num_invoice:
#                         num_invoice = self.unicode_transformation(num_invoice.upper())
                    if not num_invoice: num_invoice = ''


                    price_unit = sheet.cell(rowx=row_index,colx=int(fuel_price_unit)).value
                    if not price_unit: price_unit = 0
                    else:
                        price_unit = float(price_unit)

                    quantity = sheet.cell(rowx=row_index,colx=int(fuel_qty)).value
                    if not quantity: quantity = 0
                    else:
                        quantity = float(quantity)

                    amount = sheet.cell(rowx=row_index,colx=int(fuel_amount)).value
                    if not amount: amount = 0
                    else:
                        amount = float(amount)

                    complement_fuel = sheet.cell(rowx=row_index,colx=int(fuel_complement)).value
                    if not complement_fuel: complement_fuel = 0
                    else:
                        complement_fuel = float(complement_fuel)

                    datex = sheet.cell(rowx=row_index,colx=int(fuel_date)).value
                    print "valeur datex", datex
                    if datex :
                        date_fuel = xlrd.xldate.xldate_as_datetime(datex,book.datemode)
                        print "date_fuel", date_fuel
                    else :
                        date_fuel = None


                    hour_fuel = sheet.cell(rowx=row_index,colx=int(fuel_hour)).value
                    if not hour_fuel or hour_fuel == 'N': hour_fuel = 0
                    else:
                        hour_fuel = float(hour_fuel)


                    beneficiaire = sheet.cell(rowx=row_index,colx=int(fuel_beneficiaire)).value
                    if beneficiaire:
                        beneficiaire = self.unicode_transformation(beneficiaire.upper())
                    if not beneficiaire: beneficiaire = ''


                    panne_tableau = sheet.cell(rowx=row_index,colx=int(fuel_panne)).value
                    if panne_tableau:
                        panne_tableau = True
                    if not panne_tableau: panne_tableau = False

                    kilometrage = sheet.cell(rowx=row_index,colx=int(fuel_kilometrage)).value
                    if not kilometrage or kilometrage == 'N': kilometrage = 0
                    else:
                        kilometrage = float(kilometrage)

                    tagip = sheet.cell(rowx=row_index,colx=int(fuel_tagip)).value
                    if not tagip: tagip = 0
                    else:
                        tagip = float(tagip)

                    vehicule = sheet.cell(rowx=row_index,colx=int(fuel_vehicle_id)).value
                    print "valeur vehicule", vehicule
                    if vehicule:
                        vehicle_obj = self.env['fleet.vehicle'].search([('license_plate', 'ilike', vehicule)])
                        vehicle_id = vehicle_obj.id
                    if not vehicule:
                        vehicle_id = None


                    partenaire = sheet.cell(rowx=row_index,colx=int(fuel_partner_id)).value
                    print "valeur partenaire", partenaire
                    if not partenaire or partenaire == 'FAUX':
                        partner_id = None
                    else:
                        part = self.env['res.partner'].search([('name', 'ilike', partenaire)])
                        print "part", part
                        partner_id = part.id


                    consommation_vehicle = 0
                    if date_fuel and vehicle_id:
                        print "date_fuel", date_fuel, "vehicle_id", vehicle_id
                        date_str = str(date_fuel)
                        date_f = "'"+date_str[:10]+"'"
                        print "date_f val2===>", date_f
                        if quantity > 0:
                            if panne_tableau == True:
                                if tagip > 0:
                                    self._cr.execute("""
                                        select max(tag_ip) as distance from fleet_vehicle_fuel_gestion where to_char(date_trunc('day',date_fuel), 'YYYY-MM-DD')<="""+date_f+""" and vehicle_id="""+str(vehicle_id)+"""
                                    """)
                                    for x in self._cr.dictfetchall():
                                        di = x['distance']
                                        if not di:
                                            di = 0
                                    if di < tagip:
                                        consommation_vehicle = (float(quantity) * 100) / (float(tagip) - float(di))

                            else:
                                if kilometrage > 0:
                                    self._cr.execute("""
                                        select max(kilometrage) as distance from fleet_vehicle_fuel_gestion where to_char(date_trunc('day',date_fuel), 'YYYY-MM-DD')<="""+date_f+""" and vehicle_id="""+str(vehicle_id)+"""
                                    """)
                                    for x in self._cr.dictfetchall():
                                        di = x['distance']
                                        if not di:
                                            di = 0
                                    if di < kilometrage:
                                        consommation_vehicle = (float(quantity) * 100) / (float(kilometrage) - float(di))



                    fuel_vals = {
                        'libelle_fuel': libelle,
                        'order_number': num_order,
                        'invoice_number': num_invoice,
                        'panne_tableau': panne_tableau,
                        'tag_ip': tagip,
                        'complement_fuel': complement_fuel,
                        'consommation_vehicle': consommation_vehicle,
                        'vehicle_id': vehicle_id,
                        'date_fuel': date_fuel,
                        'beneficiaire': beneficiaire,
                        'kilometrage': kilometrage,
                        'amount_fuel': amount,
                        'price_per_liter': price_unit,
                        'qty_fuel': quantity,
                        'hour_fuel': hour_fuel,
                        'partner_id': partner_id
                    }
                    print "fuel_vals", fuel_vals

                    self.env['fleet.vehicle.fuel.gestion'].create(fuel_vals)



        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
         }
