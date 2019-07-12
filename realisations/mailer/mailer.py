# -*- coding: utf-8 -*-
from smtp_mail import SMTP
import pymongo
from database import Database
from settings import email_password, api_url
import requests
from datetime import datetime, timedelta
import time


def get_events_for_user(user):
    events = []
    for wish in user['wish_list']:
        begin = datetime.today()
        end = begin + timedelta(days=wish['event_time_before'])
        ut_begin = int(time.mktime(begin.timetuple()))
        ut_end = int(time.mktime(end.timetuple()))

        url = api_url + f'event?type={wish["type_event"]}&street={user["street"]}&begin={ut_begin}&end={ut_end}'
        if(user.get('house') is not None):
            url += f'&house={user["house"]}'
        response = requests.get(url)
        events += list(response.json().values())
    return events


def gen_message(user, events):
    months = {
        1: "января",
        2: "февраля",
        3: "марта",
        4: "апреля",
        5: "мая",
        6: "июня",
        7: "июля",
        8: "августа",
        9: "сентября",
        10: "октября",
        11: "ноября",
        12: "декабря"
    }
    message = f""" 
Здравствуйте {user['name']}.

Хотим проинформировать в с обинтересующих вас событиях:\n\n
"""
    for event in events:
        begin = datetime.utcfromtimestamp(event['begin'])
        event_string = f"С {begin.day} {months[begin.month]} {begin.year} года"
        if(event.get('end') is not None):
            end = datetime.utcfromtimestamp(event['end'])
            event_string += f" до {end.day} {months[end.month]} {end.year} года"
        event_string += f" произойдет {event['description']} по адресу {event['text']}"
        message += event_string + "\n\n"
    return message


if __name__ == "__main__":
    smtp_obj = SMTP("no-repy@gradintegra.com", email_password)
    db = Database()
    cursor = db.get_cursor()
    title = "Gradinformer оповещение"

    for user in cursor:
        events = get_events_for_user(user)
        if(len(events)):
            message = gen_message(user, events)
            smtp_obj.send_message(user['email'], message, title)
