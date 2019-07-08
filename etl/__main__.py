#!/usr/bin/python
# -*- coding: utf-8 -*-
from parsers.energy_sochi import get_info_on_day
from database.database import Database
from mailer.mailer import send_messages
from datetime import datetime, timedelta

if __name__ == '__main__':

    db = Database()
    try:
        db.load_engergy_data(get_info_on_day())
        db.delete_old_than_date(datetime.today())
        
        dhu_torday_and_yestorday = db.get_information_on_days(datetime.today(), datetime.today() + timedelta(days=1))
        send_messages(db.get_users_match_data(dhu_torday_and_yestorday))
    finally:
        db.close() 