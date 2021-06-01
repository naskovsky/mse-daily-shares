from tabulate import tabulate
import datetime
import requests
import pandas as pd
import os
from xml.etree import ElementTree
from zeep import Client

sharequantity = input("plase enter the quantity of shares: ")

URL = "https://www.mse.mk/Repository/Reports/2021/"


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


# getting the dates for the functions
x = datetime.datetime.now()
day = x.strftime("%d")
month = x.strftime("%m")
year = x.strftime("%Y")
date_format = day + "." + month + "." + year + "en.xls"
datum = day + "." + month + "." + year
week_day = x.strftime("%A")
week_day_number = x.strftime("%w")
n = int(week_day_number)
download_link = ""


def get_friday_date():
    day_change = 0
    if week_day_number == "6":
        day_change = int(day) - 1
        # print(day_change)
    if week_day_number == "0":
        day_change = int(day) - 2
        # print(day_change)
    day_change_str = str(day_change)
    if day_change < 10:
        day_change_str = "0" + str(day_change)
    return day_change_str


def get_weekday_macedonian():
    weekday_macedonian = ""
    if week_day_number == "6" or week_day_number == "0":
        weekday_macedonian = "Петок"
    elif week_day_number == "1":
        weekday_macedonian = "Понеделник"
    elif week_day_number == "2":
        weekday_macedonian = "Вторник"
    elif week_day_number == "3":
        weekday_macedonian = "Среда"
    elif week_day_number == "4":
        weekday_macedonian = "Четврток"
    elif week_day_number == "5":
        weekday_macedonian = "Петок"
    return weekday_macedonian


def get_download_link_weekend():
    date_format_weekend = get_friday_date() + "." + month + "." + year + "en.xls"
    download_link_weekend = URL + date_format_weekend
    return download_link_weekend


if 0 < n < 6:  # work days
    date_format = day + "." + month + "." + year + "en.xls"
    # print(date_format)
    download_link = URL + date_format
else:  # weekend
    date_format = get_friday_date() + "." + month + "." + year + "en.xls"
    download_link = get_download_link_weekend()

# downloads the xls file from mse that contains the daily prices of the shares
r = requests.get(download_link, allow_redirects=True)
open(date_format, 'wb').write(r.content)

# reads the xls file and stores it in df
df = pd.read_excel(date_format)

# makes soap request to nbrm and recieves a xml file
client = Client(wsdl='https://www.nbrm.mk/klservice/kurs.asmx?WSDL')
price_list = client.service.GetExchangeRate(datum, datum).encode()

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
# print(' * {} {}'.format(
# oznaka, cena
# ))

daily_price = df.iat[4, 1]
percentile_change = df.iat[4, 2]
if percentile_change > 0:
    percentile_change = "+" + str(percentile_change)
max_price = df.iat[4, 5] * int(sharequantity)
min_price = df.iat[4, 6] * int(sharequantity)
avg_price_denar = (df.iat[4, 1] * int(sharequantity))
avg_price_euro = (df.iat[4, 1] * int(sharequantity)) / float(niza[0].vrati_cena())
avg_price_dollar = (df.iat[4, 1] * int(sharequantity)) / float(niza[1].vrati_cena())
dividend = 550 * int(sharequantity)
dividend_euro = dividend / float(niza[0].vrati_cena())
dividend_dollar = dividend / float(niza[1].vrati_cena())


def get_trading_date():
    if 0 < n < 6:  # work days
        return day + "." + month + "." + year
    else:  # weekend
        return get_friday_date() + "." + month + "." + year


# TODO: weekend date evaluator for last friday
print("Датум: " + get_trading_date())
print("Trading day: " + get_weekday_macedonian())
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
