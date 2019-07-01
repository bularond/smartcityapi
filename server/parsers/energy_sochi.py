import requests
from bs4 import BeautifulSoup
from datetime import date, datetime
import re
from copy import copy


url_sochi_news = "https://sochi.com/news/search/index.php?q=%D0%BE%D1%82%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%BD%D0%B8%D0%B5+%D1%81%D0%B2%D0%B5%D1%82%D0%B0&s=%D0%9D%D0%B0%D0%B9%D1%82%D0%B8"    

def get_new_url_with_current_date(date):
    page = requests.get(url_sochi_news)
    soup = BeautifulSoup(page.text, 'html.parser')

    news_list = soup.find(class_='search-page')

    urls = []
    for news_item in news_list.find_all('a'):
        if(len(news_item.attrs['href'].split('/')) > 3 and news_item.attrs['href'].find("search") == -1):
            urls.append("https://sochi.com" + news_item.attrs['href'])

    point = 0
    for news_item in news_list.find_all('small'):
        if(news_item.contents[0].find("Изменен") != -1):
            news_date = list(map(int, news_item.contents[0].split()[-1].split('.')))
            if(news_date == [date.day, date.month, date.year]):
                return urls[point]
            
            point += 1

    return None

def get_today_info():
    """
    Возвращает лист словарей['begin', 'end', 'streets', 'type']
    """

    url = get_new_url_with_current_date(date.today())

    if(url != None):
        data = []

        def str_list_to_datetime(ls):
            month = {
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
            hour, minute = map(int, ls[2].split('.'))
            return datetime(date.today().year, month[ls[1]], int(ls[0]), hour, minute)

        def str_to_streets(st, dict_with_date):

            # убираю все скобочки
            while(st.count('(')):
                st = st[:st.find('(')-1] + st[st.find(')')+1:]

            # разделяю по ', ' и '; '
            ls = '; '.join(st.split(', ')).split('; ')

            '''
            Шаблоны встречающихся объектов

            ул.Фурманова
            форелевый завод
            в поселке Бестужевское ул.Дубравская
            ул.Воровского №№20 - 40
            в мкр Дагомыс Барановское шоссе 
            проспект Октябрьский 
            '''
            #TODO сделать обработку проспектов и преулков
            for part in ls:
                if(part.find('ул.') != -1):
                    dict_with_street = dict_with_date.copy()
                    dict_with_street['street'] = re.search(r'ул.[^№]+', part)[0][3:-1]
                    #если указано несколько домов
                    if(re.search(r'№№[0-9]+ - [0-9]+', part)):
                        match = re.search(r'№№\d+ - \d+', part)[0]
                        start, _, end = match[2:].split()
                        start, end = int(start), int(end)

                        for home_number in range(start, end + 1):
                            dict_with_number = copy(dict_with_street)
                            dict_with_number['home_number'] = home_number
                            data.append(dict_with_number)
                    #если указан 1 дом
                    elif(re.search(r'№[0-9]+', part)):
                        match = re.search(r'№[0-9]+', part)[0]
                        home_number = match[0][1:]

                        dict_with_number = copy(dict_with_street)
                        dict_with_number['home_number'] = home_number
                        data.append(dict_with_number)
                    #значит дома не указаны, добавляем с 'home_number' = 0
                    else:
                        data.append(dict_with_street)


        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        text_list = soup.find(class_='detail_text text-justify')

        flag = True

        dict_with_date = {'begin':None, 'end':None, 'street': '', 'home_number': 0, 'type': 'energy'}
        for text_item in text_list.find_all('p')[:-1]:
            if (flag):
                dict_with_date = {'begin': None, 'end': None, 'street': '', 'home_number': 0, 'type': 'energy'}
                text = text_item.contents[0].split()
                dict_with_date['begin'] = str_list_to_datetime(text[:2] + [text[3]])
                dict_with_date['end'] = str_list_to_datetime(text[:2] + [text[5]])
            else:
                text = text_item.contents[0][4:-3]
                str_to_streets(text, dict_with_date)
            flag = not flag
        
        return data

if __name__ == "__main__":
    f= open('cash/data.txt', 'w')
    f.write('\n\n'.join(map(str, get_today_info())))