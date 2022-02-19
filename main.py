from tabulate import tabulate
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
from xml.etree import ElementTree
from zeep import Client

share_name = input("Enter the name of the stock: ")
stockquantity = input("Enter the quantity of shares: ")

base_url = "https://www.mse.mk"


class KursKlasa:

    def __init__(self, _oznaka, _cena):
        self.oznaka = _oznaka
        self.cena = _cena

    def vrati_oznaka(self):
        return self.oznaka

    def vrati_cena(self):
        return self.cena

    def pecati_dvete(self):
        return self.oznaka + " " + self.cena

# gets the contents of the href in the a tag
content = requests.get(base_url)
soup = BeautifulSoup(content.text, 'html.parser')
find_a = soup.find_all('a')
temp = find_a[4]
base_url = base_url + temp['href']

# date formatting
date = base_url[43:53]
# "mk.xls" needed so it can read from file
date_format = date + "mk.xls"
date_weekday = pd.Timestamp(date)

download_link = base_url

# downloads the xls file from mse that contains the daily prices of the shares
r = requests.get(download_link, allow_redirects=True)
open(date_format, 'wb').write(r.content)

# reads the xls file and stores it in df
df = pd.read_excel(date_format)

# makes soap request to nbrm and recieves a xml file
client = Client(wsdl='https://www.nbrm.mk/klservice/kurs.asmx?WSDL')
price_list = client.service.GetExchangeRate(date, date).encode()

# saving the xml file
file = open('kursna_lista.xml', 'wb')
file.write(price_list)
file.close()

# reading the xml file
file_name = 'kursna_lista.xml'
dom = ElementTree.parse(file_name)
kursevi = dom.findall('KursZbir')

niza = []

for kurs in kursevi:

    oznaka = kurs.find('Oznaka').text
    cena = kurs.find('Sreden').text
    if oznaka == 'EUR' or oznaka == 'USD':
        niza.append(KursKlasa(oznaka, cena))

# declaring the variables for global use
daily_price = 0

for x in range(4, 304):
    ime = df.iat[x, 0].lower()
    if share_name in ime:
        daily_price = df.iat[x, 1]
        percentile_change = df.iat[x, 2]
        if percentile_change > 0:
            percentile_change = "+" + str(percentile_change)
        max_price = (df.iat[x, 5] * int(stockquantity))
        min_price = (df.iat[x, 6] * int(stockquantity))
        avg_price_denar = (daily_price * int(stockquantity))
        avg_price_euro = (daily_price * int(stockquantity)) / float(niza[0].vrati_cena())
        avg_price_dollar = (daily_price * int(stockquantity)) / float(niza[1].vrati_cena())
        dividend = 550 * int(stockquantity)
        dividend_euro = dividend / float(niza[0].vrati_cena())
        dividend_dollar = dividend / float(niza[1].vrati_cena())
        break

try:
    daily_price
except NameError:
    print("Akcijata koja ja pobaravte, ne e pronajdena!")
    exit(-1)

# TODO: weekend date evaluator for last friday
print("Датум: " + date)
print("Trading day: " + str(date_weekday.day_name()))
print(
    "*********************************************************************************************************************************************************************************")


def print_dialy_price():
    data = {"Дневна цена": ["Ден - {:,.2f}".format(daily_price)],
            "Вкупно денари": ["Ден - {:,.2f}".format(avg_price_denar)],
            "Евра": ["€{:,.2f}".format(avg_price_euro)],
            "Долари": ["${:,.2f}".format(avg_price_dollar)],
            "% Change": [percentile_change],
            "Евро курс": ["Ден - {:,.4f}".format(float(niza[0].vrati_cena()))],
            "Долар курс": ["Ден - {:,.4f}".format(float(niza[1].vrati_cena()))],
            "Дивидена - 2020": ["Ден - 550"],
            "Дивиденда денари": ["Ден - {:,.2f}".format(dividend)],
            "Дивиденда евро": ["€{:,.2f}".format(dividend_euro)],
            "Дивиденда долар": ["${:,.2f}".format(dividend_dollar)]}
    return tabulate(data, headers="keys", tablefmt="pretty")


print(print_dialy_price())

# remove the xls and xml files from the directory
os.remove(file_name)
os.remove(date_format)
