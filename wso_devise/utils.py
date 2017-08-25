# -*- coding: utf-8 -*-
import re
from urllib2 import urlopen
from bs4 import BeautifulSoup
from openerp.exceptions import UserError
from openerp import _
import logging
_logger = logging.getLogger(__name__)


class CurrencyServices:


	"""
	Access to the website to get html code as String
	"""
	def extract_data_website_toString(self, url):
		html = ''
		try:
			html = urlopen(url).read()
		except Exception as e:
			raise UserError(_("Malagasy Central Bank website currently unvailable"))
		return html

	"""
	Change the string code to hierarchic tree with BeautifulSoup
	"""
	def string_to_hierarchy(self, data):
		soup = ""
		try:
			soup = BeautifulSoup.BeautifulSoup(data)
		except Exception as e:
			raise UserError(_('Unrecognized data website !'))
		return soup

	"""
	Extract the currency table from the tree  using one of currency as references to find all of them
	here we used 'DKK'
	"""
	def extract_currency_table(self, soup):
		pattern = re.compile(r'DKK')
		oneCurrency = soup.find(text=pattern)
		myTable = oneCurrency.parent.parent.parent
		return myTable

	"""
	Transform the html table to python array
	"""
	def datatable_to_array(self, dataTable):
		listCurrency = {}
		for row in dataTable.contents:
		    if len(row.contents) == 2:
		    	curr = row.contents[0].getText()
		        try:
		            value = row.contents[1].getText().replace(" ", "").replace(",", ".")
		            value = float(value)
		            listCurrency[curr] = value
		        except Exception as e:
		            raise UserError(_('Data value error of one or more currency :'))
		if not listCurrency.has_key('USD') and not listCurrency.has_key('EUR'):
			raise UserError(_('Error of Data, not found EUR and USD'))
		return listCurrency


	"""
	Calculate the value of each currency depending on the main currency
	"""
	def calculate_currency_change(self, list_currency, main_currency):
		if main_currency == 'MGA':
			list_currency['MGA'] = 1
			for curr in list_currency:
				list_currency[curr] = 1/list_currency[curr]
		else :
			ref = list_currency[main_currency]
			list_currency['MGA'] = ref
			for curr in list_currency:
				if curr == main_currency:
					list_currency[curr] = 1
				elif curr == 'MGA':
					pass
				else:
					list_currency[curr] = ref/list_currency[curr]



