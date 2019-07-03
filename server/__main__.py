from parsers.energy_sochi import get_today_info
from database.database import Database
from mailer.mailer import send_messages
from datetime import timedelta

if __name__ == '__main__':
    db = Database()
    db.load_engergy_data(get_today_info())
    db.delete_old_data()

    dhu_yesterday = db.get_information_on_day(timedelta(day = 1))
    send_messages(db.get_users_match_data(dhu_yesterday))

    db.close()