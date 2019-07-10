import requests
import re
from datetime import datetime, timedelta
import time
from settings import sity
from yandex_geocoder.yandex_geocoder import str_to_geo_data
from copy import copy

url = "https://pdo.gridcom-rt.ru/Ajax/Interruptions?region=&district=&settlement=&manualSettlement=&street=&manualStreet=&house=&from=%s&to=%s&fieldName=&orderDirection=0&page=%d&isSettlement=true&isManualStreet=true"

def str_to_unix_time(st):
    # 01 июля 2019, 08:00

    months = {
            "января": 1,
            "февраля": 2,
            "марта": 3,
            "апреля": 4,
            "мая": 5,
            "июня": 6,
            "июля": 7,
            "августа": 8,
            "сентября": 9,
            "октября": 10,
            "ноября": 11,
            "декабря": 12
        }

    day, month, year, times = st.split()

    day = int(day)
    month = months[month]
    year = int(year[:-1])
    hour, minute = map(int, times.split(':'))

    return int(time.mktime(datetime(year, month, day, hour, minute).timetuple()))

def get_data_on_mounth(begin_month):
    now_date = copy(begin_month)
    data = []

    dict_template = {
        'type': 'energy',
        'description': 'Отклчение водоснабжения',
        'contact_information': 'ОАО «Сетевая компания», телефон 8 (800) 20-00-878'
    }

    while(now_date.month == begin_month.month):
        date_str = f"{now_date.day}.{now_date.month}.{now_date.year}"

        page_number = 1

        while(True):
            now_url = url % (date_str, date_str, page_number)
            response = requests.get(now_url)
            page = response.json()

            if(len(page['items']) == 0):
                break
            else:
                items = page['items']
                for item in items:
                    geodata = str_to_geo_data(item['Address'])
                    if(len(geodata)):
                        event = geodata[0]
                        event['begin'] = str_to_unix_time(item['From'])
                        event['end'] = str_to_unix_time(item['To'])
                        event.update(dict_template)
                    
                    data.append(event)

            print(page_number, now_date)
            page_number += 1

        now_date += timedelta(days=1)

    return data

