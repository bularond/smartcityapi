#!/usr/bin/python
# -*- coding: utf-8 -*-
from parsers.energy_kazan import get_data_from_day
from datetime import datetime, timedelta
from database import Database
import time

if __name__ == '__main__':
    db = Database()
    start_time = time.time()
    data = get_data_from_day(datetime(2019, 5, 7))
    db.load_data(data)
    print(time.time() - start_time)
    print(len(data))