from tabulate import tabulate
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import json

share_name = input("Внесете го името на акцијата: ").strip()
stockquantity = input("Внесете ја количината на акции: ").strip()

base_url = "https://www.mse.mk"

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

# loads the json
kl_json = json.loads(requests.get(
    f"https://www.nbrm.mk/KLServiceNOV/GetExchangeRates?StartDate={date}&EndDate={date}&format=json").text)

# filters only eur and usd currency info
kl_dict = {item['oznaka']: item['prodazen'] for item in kl_json if item['oznaka'] in ['EUR', 'USD']}

euro = float(kl_dict['EUR'])
dollar = float(kl_dict['USD'])

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
        # avg_price_euro = (daily_price * int(stockquantity)) / float(niza[0].vrati_cena())
        avg_price_euro = (daily_price * int(stockquantity)) / euro
        # avg_price_dollar = (daily_price * int(stockquantity)) / float(niza[1].vrati_cena())
        avg_price_dollar = (daily_price * int(stockquantity)) / dollar
        dividend = 550 * int(stockquantity)
        dividend_euro = dividend / euro
        dividend_dollar = dividend / dollar
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
            "Евро курс": ["Ден - {:,.4f}".format(euro)],
            "Долар курс": ["Ден - {:,.4f}".format(dollar)],
            "Дивидена - 2020": ["Ден - 550"],
            "Дивиденда денари": ["Ден - {:,.2f}".format(dividend)],
            "Дивиденда евро": ["€{:,.2f}".format(dividend_euro)],
            "Дивиденда долар": ["${:,.2f}".format(dividend_dollar)]}
    return tabulate(data, headers="keys", tablefmt="pretty")


print(print_dialy_price())

# remove the xls file from the directory
os.remove(date_format)
