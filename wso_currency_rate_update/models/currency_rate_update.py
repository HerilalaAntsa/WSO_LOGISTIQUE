# -*- coding: utf-8 -*-
# © 2009-2016 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
import re
from urllib2 import urlopen
from bs4 import BeautifulSoup as Soup
import logging
import datetime
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)



class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    # Activate the currency update
    auto_currency_up = fields.Boolean(
        string='Automatic Currency Rates Update', default=True,
        help="Automatic download of currency rates from the source www.banque-centrale.mg ")

    """
    Access to the website to get html code as String
    """
    def extract_data_website_toString(self,url):
        html = ''
        try:
            html = urlopen(url).read()
        except UserError:
            raise UserError(_('Malagasy Central Bank website currently unvailable.'))
        return html

    """
    Change the string code to hierarchic tree with BeautifulSoup
    """
    def string_to_hierarchy(self,data):
        soup = ""
        try:
            soup = Soup(data, "lxml")
        except UserError:
            raise UserError(_('Unrecognized data website !'))
        return soup

    """
    Extract the currency table from the tree  using one of currency as references to find all of them
    here we used 'DKK'
    """
    def extract_currency_table(self,soup):
        pattern = re.compile(r'DKK')
        if not pattern:
            raise UserError(_('ERROR: Maybe the Malagasy Central Bank website has been updated !'))
        oneCurrency = soup.find(text=pattern)
        myTable = oneCurrency.parent.parent.parent
        return myTable

    """
    Find current Date
    """
    def find_date(self,table):
        s = Soup(str(table.parent), "lxml")
        tab = s.findAll("strong")
        match = re.search(r'(\d+/\d+/\d+)', str(tab[0]))

        periode_actuelle = datetime.datetime.now()
        annee = periode_actuelle.year
        date_convert = str(match.group(1))
        if(len(date_convert) < 10):
            temp = date_convert[-2:]
            date_convert = date_convert[:6]+str(annee)
        return datetime.datetime.strptime(date_convert, '%d/%m/%Y').strftime('%Y-%m-%d')


    """
    Transform the html table to python array
    """
    def datatable_to_array(self,dataTable):
        listCurrency = {}
        for row in dataTable.contents:
            if len(row.contents) == 2:
                curr = row.contents[0].getText()
                try:
                    value = row.contents[1].getText().replace(" ", "").replace(",", ".")
                    value = float(value)
                    listCurrency[curr] = value
                except UserError:
                    raise UserError(_('Data value error of one or more currency !'))
        if not listCurrency.has_key('USD') and not listCurrency.has_key('EUR'):
            raise UserError(_('Error of Data, not found EUR and USD'))
        return listCurrency

    @api.multi
    def update_currency_rate_sql(self, date, rates):
        currency_pool = self.env["res.currency.rate"]
        currency_pool_name = self.env["res.currency"]
        for key, value in rates.items():
            try:
                print key + " : " + str(value)
                id_rate = (currency_pool_name.search([("name", "=", key)]))[0].id
                print date
                currency_rate = currency_pool.search([("name", "=", str(date)),("currency_id", "=", id_rate)])
                if currency_rate:
                    for cur in currency_rate:
                        cur.write({'rate':value})
                else:
                    currency_pool.create({'name': str(date), 'currency_id': id_rate, 'rate': value})
            except UserError:
                raise UserError(_('Some errors occur when updating the rate of : ' + key))

    """
    Main function : Run the currency update
    """
    @api.multi
    def run_currency_update(self):
        url="http://www.banque-centrale.mg"
        string_data = self.extract_data_website_toString(url)
        soup = self.string_to_hierarchy(string_data)
        myTable = self.extract_currency_table(soup)
        date = self.find_date(myTable)
        listCurrency = self.datatable_to_array(myTable)
#         As we are just interested on EUR and USD rates
        rates = dict((k, listCurrency[k]) for k in ('EUR', 'USD'))
        self.update_currency_rate_sql(date, rates)


