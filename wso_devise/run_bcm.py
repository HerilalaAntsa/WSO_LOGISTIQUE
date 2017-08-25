# -*- coding: utf-8 -*-
import re
from urllib2 import urlopen
from bs4 import BeautifulSoup as Soup
import datetime
import logging
_logger = logging.getLogger(__name__)

"""
Access to the website to get html code as String
"""
def extract_data_website_toString(url):
    html = ''
    try:
        html = urlopen(url).read()
    except Exception as e:
        raise Exception(_("Malagasy Central Bank website currently unvailable"))
    return html

"""
Change the string code to hierarchic tree with BeautifulSoup
"""
def string_to_hierarchy(data):
    soup = ""
    try:
        soup = Soup(data, "lxml")
    except Exception as e:
        raise e('Unrecognized data website !')
    return soup

"""
Extract the currency table from the tree  using one of currency as references to find all of them
here we used 'DKK'
"""
def extract_currency_table(soup):
    pattern = re.compile(r'DKK')
    oneCurrency = soup.find(text=pattern)
    myTable = oneCurrency.parent.parent.parent
    return myTable

"""
Find current Date
"""
def find_date(table):
    s = Soup(str(table.parent), "lxml")
    tab = s.findAll("strong")
    match = re.search(r'(\d+/\d+/\d+)', str(tab[0]))
    return match.group(1)

"""
Transform the html table to python array
"""
def datatable_to_array(dataTable):
    listCurrency = {}
    for row in dataTable.contents:
        if len(row.contents) == 2:
            curr = row.contents[0].getText()
            try:
                value = row.contents[1].getText().replace(" ", "").replace(",", ".")
                value = float(value)
                listCurrency[curr] = value
            except Exception as e:
                raise Exception('Data value error of one or more currency :')
    if not listCurrency.has_key('USD') and not listCurrency.has_key('EUR'):
        raise Exception('Error of Data, not found EUR and USD')
    return listCurrency


"""
Calculate the value of each currency depending on the main currency
"""
def calculate_currency_change(list_currency, main_currency):
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

url="http://www.banque-centrale.mg"
string_data = extract_data_website_toString(url)
soup = string_to_hierarchy(string_data)
myTable = extract_currency_table(soup)
date = find_date(myTable)
listCurrency = datatable_to_array(myTable)
dict = dict((k, listCurrency[k]) for k in ('EUR', 'USD'))
for key, value in dict.items():
    print key + " : " + str(value)
print dict
print "date = "+date
print "USD = "+ str(listCurrency["USD"])
print "EUR = "+ str(listCurrency["EUR"])
# calculate_currency_change(listCurrency, main_currency)

periode_actuelle = datetime.datetime.now()
annee = periode_actuelle.year
date_convert = str(date)
if(len(date_convert) < 10):
    temp = date_convert[-2:]
    date_convert = date_convert[:6]+str(annee)
date_convert = datetime.datetime.strptime(date_convert, '%d/%m/%Y').strftime('%Y-%m-%d')


print date_convert

