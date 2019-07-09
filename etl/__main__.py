#!/usr/bin/python
# -*- coding: utf-8 -*-
from parsers.energy_sochi import get_info_on_day
from database import Database
from datetime import datetime, timedelta
from yandex_geocoder.yandex_geocoder import str_to_geo_data

if __name__ == '__main__':
    '''
    db = Database()
    try:
        energy_data = get_info_on_day(datetime(year=2019, mouth=7, day=4, hour=12))
        db.load_data(energy_data)
        #db.delete_old_than_date(datetime.today())
    finally:
        db.close()
    '''
    print(*str_to_geo_data("сочи  ул.Земляничная"), sep = '\n')