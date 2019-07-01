from parsers.energy_sochi import get_today_info
from database.database import load_engergy_data

if __name__ == '__main__':
    load_engergy_data(get_today_info())