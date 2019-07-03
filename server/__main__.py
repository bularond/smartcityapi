from parsers.energy_sochi import get_today_info
from database.database import Database

if __name__ == '__main__':
    db = Database()
    db.load_engergy_data(get_today_info())
    db.delete_old_data()
    db.close()