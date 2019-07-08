#!/usr/bin/python
# -*- coding: utf-8 -*-
from parsers.energy_sochi import get_info_on_day
from database import Database
from datetime import datetime, timedelta

if __name__ == '__main__':
    db = Database()
    try:
        energy_data = get_info_on_day(datetime.today())
        db.load_data(energy_data)
        db.delete_old_than_date(datetime.today())
    finally:
        db.close() 