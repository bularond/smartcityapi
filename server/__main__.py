#!/usr/bin/python
# -*- coding: utf-8 -*-
from parsers.energy_sochi import get_info_on_day
from database.database import Database
from mailer.mailer import send_messages
import mailer.smtp_mail 
from datetime import datetime

if __name__ == '__main__':

    db = Database()
    db.load_engergy_data(get_info_on_day())
    db.delete_old_than_date(datetime.today())

    dhu_yesterday = db.get_information_on_day()
    #send_messages(db.get_users_match_data(dhu_yesterday))

    db.close()