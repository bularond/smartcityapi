import requests
from bs4 import BeautifulSoup as bs
import re
from datetime import datetime, timedelta
import time
from settings import sity
from yandex_geocoder.yandex_geocoder import str_to_geo_data

url_kazan_news = "https://www.kzn.ru/meriya/press-tsentr/novosti/?ALL_FIELDS=%D0%9E%D0%BF%D1%83%D0%B1%D0%BB%D0%B8%D0%BA%D0%BE%D0%B2%D0%B0%D0%BD+%D0%B3%D1%80%D0%B0%D1%84%D0%B8%D0%BA&DATE_FROM=&DATE_TO=&PROPERTY_REF_NR=-1&submit=Y"

def str_from_news_to_datetime(st):
    """
    26.06.2019, 09:46   =>   <datetime>
    """
    day, time = st.split(', ')
    return datetime(*map(int, day.split('.')[::-1]), *map(int, time.split(':')))

def get_news_from_day(requests_day):
    page = requests.get(url_kazan_news)
    soup = bs(page.text, 'html.parser')
    news_list = soup.find(class_='news-lists-bl')

    requested_url = ''
    for news in news_list.find_all(class_="news-lists__descr"):
        contents = news.contents[1::2]
        news_day = str_from_news_to_datetime(contents[0].text)
        if(requests_day - news_day < timedelta(days=1)):
            return contents[1].contents[1].attrs['href']
    else:
        return None

def get_data_from_day(requests_day):
    url = get_news_from_day(requests_day)
    
    if(url != None):
        url = 'https://www.kzn.ru' + url
        page = requests.get(url)
        soup = bs(page.text, 'html.parser')
        information_list = soup.find(class_='detailText')

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
        months_list = '(' + '|'.join(list(months.keys())) + ')'

        output_data = []
        dict_template = {
            'type': 'energy',
            'description': 'Отключение водоснабжения',
            'contact_information': ''
        }
        dict_template_with_dates = dict_template.copy()
        active = False
        for paragraph in information_list.find_all('p'):
            if(re.search(r'^\nВ связи', paragraph.text)):
                active = True
                # с 22 июля по 4 августа
                if(re.search(rf'с [0-9]+ {months_list} по [0-9]+ {months_list}', paragraph.text)):
                    match = re.search(rf'с [0-9]+ {months_list} по [0-9]+ {months_list}', paragraph.text)[0]
                    match = match.split()
                    begin = datetime(datetime.today().year, months[match[2]], int(match[1]))
                    end   = datetime(datetime.today().year, months[match[5]], int(match[4]))
                    dict_template_with_dates['begin'] = int(time.mktime(begin.timetuple()))
                    dict_template_with_dates['end'] = int(time.mktime(end.timetuple()))
                # с 8 по 10 июля
                elif(re.search(rf'с [0-9]+ по [0-9]+ {months_list}',  paragraph.text)):
                    match = re.search(rf'с [0-9]+ по [0-9]+ {months_list}',  paragraph.text)[0]
                    match = match.split()
                    begin = datetime(datetime.today().year, months[match[4]], int(match[1]))
                    end   = datetime(datetime.today().year, months[match[4]], int(match[3]))
                    dict_template_with_dates['begin'] = int(time.mktime(begin.timetuple()))
                    dict_template_with_dates['end'] = int(time.mktime(end.timetuple()))
            elif(active):
                text = ''.join(filter(
                    lambda char: 
                        re.search(r'[А-Яа-я0-9,]', char),
                    paragraph.text
                ))
                street, *houses = text.split(',')
                for house in houses:
                    geodata = str_to_geo_data(f'{sity} {street} {house}')
                    if(len(geodata)):
                        data = geodata[0]
                        data.update(dict_template_with_dates)
                        output_data.append( data )
        
        return output_data
    else:
        return None

if __name__ == '__main__':
    print(*get_data_from_day(datetime(2019, 6, 26, 0, 0)), sep = '\n')
