# -*- coding: utf-8 -*-
from openerp.addons.currency_rate_update import services
from urllib2 import urlopen
from openerp import _
from openerp.exceptions import UserError
import re
from .utils import CurrencyServices
import logging
_logger = logging.getLogger(__name__)


class BCMGetter(services.currency_getter_interface.CurrencyGetterInterface):
	code = 'BCM'
	name = 'Malagasy Central Bank'

	supported_currency_array = [
        "AUD", "EUR", "USD", "GBP", "CHF", "JPY", "CAD", "DKK", "NOK", "SEK",
        "DJF", "XDR", "MUR", "ZAR", "AUD", "HKD", "SGD", "NZD", "INR", "CNY", "MGA"]


	def get_updated_currency(self, currency_array, main_currency,max_delta_days):
		url="http://www.banque-centrale.mg"
		self.validate_cur(main_currency)

		string_data = CurrencyServices().extract_data_website_toString(url)
		soup = CurrencyServices().string_to_hierarchy(string_data)
		myTable = CurrencyServices().extract_currency_table(soup)  
		listCurrency = CurrencyServices().datatable_to_array(myTable)
		CurrencyServices().calculate_currency_change(listCurrency, main_currency)

		if main_currency in currency_array:
		    currency_array.remove(main_currency)
		for curr in currency_array:
			if not listCurrency.has_key(curr):
				# raise Exception('Malagasy Current update doesn t support one of selected currency :', curr)
				raise UserError(_('There are currency not supported'))
			else :
				self.updated_currency[curr] = listCurrency[curr]
		return self.updated_currency, self.log_info
                
