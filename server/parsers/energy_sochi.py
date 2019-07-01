import requests
from bs4 import BeautifulSoup
from datetime import date, datetime


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
    Возвращает лист словарей['begin', 'end', 'streets']
    """
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

    def str_to_streets(st):
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
        '''
        return ls
        

    url = get_new_url_with_current_date(date.today())
    
    if(url != None):
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        text_list = soup.find(class_='detail_text text-justify')

        data = []
        flag = True
        for text_item in text_list.find_all('p')[:-1]:
            if (flag):
                data.append(dict())
                text = text_item.contents[0].split()
                data[-1]['begin'] = str_list_to_datetime(text[:2] + [text[3]])
                data[-1]['end'] = str_list_to_datetime(text[:2] + [text[5]])
            else:
                text = text_item.contents[0][4:-3]
                data[-1]['streets'] = str_to_streets(text)
            flag = not flag
        
        return data

if __name__ == "__main__":
    print(*get_today_info(), sep = '\n\n')