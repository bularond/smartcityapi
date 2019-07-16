import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from settings import vk_api_key, api_url
from threading import Thread
import requests
import json
from random import randint
from database import Database
from yandex_geocoder import str_to_geo_data


def get_pages(lst, count):
    offset = 0
    pages = []
    while(offset < len(lst)):
        pages.append(lst[offset:offset+count])
        offset += count
    return pages


def add_in_wishlist(user, event_type, event_time_before):
    print(user['user_id'], event_type, event_time_before)

data_set = {
    'ЖКХ': [
        ['water', "Отключение воды"],
        ['energy', "Отключение электричества"]
    ],
    'Мероприятия': [
        ['koncert', 'Концерт'],
        ['open_door_day', 'День открытых дверей'],
        ['theater', 'Пьесса']
    ]
}

def menu(user, old_payload = None):
    '''
    Принемает на вход данные с нажатой кнопки.
    Возвращает dict с полями 
    > update_alert_time
    > update_wish_list
    > waiting_adress
    > keypad
    > message
    Чтобы прочесть этот моудуль, надо свернуть все и понять общую структуру
    '''
    if(old_payload == None):
        old_payload = '{"val": "return", "prnt": {"title": "main", "page": 0, "val": "", "prnt":{}}, "title": "sub", "page": 0}'
    else:
        old_payload = old_payload.replace("'", '"')

    old_payload = json.loads(old_payload)
    new_payload = {
        'title': old_payload['title'],
        'page': old_payload['page'],
        'prnt': old_payload.get('prnt')
    }
    output = {
        'message': ''
    }

    # Реагирование на кнопку, определение новой клавиатуры
    if  (old_payload['title'] == 'main'):
        if(old_payload['val'] == 'sub'):
            new_payload['title'] = 'sub'
            output['message'] = 'Список категорий.\nНажмите, чтобы посмотреть список событий по данной категории.'
        elif(old_payload['val'] == 'alert_time'):
            new_payload['title'] = 'alert_time'
            output['message'] = 'Выберете время, в которое будут приходить сообщения.'
        elif(old_payload['val'] == 'unsub'):
            new_payload['title'] = 'unsub'
            output['message'] = 'Список ваших подписок.\nНажмите, чтобы отписаться.'
        elif(old_payload['val'] == 'adr_change'):
            new_payload['title'] = 'adr_change'
            output['waiting_adress'] = True
        new_payload['page'] = 0
        new_payload['prnt'] = old_payload.copy()
    elif(old_payload['title'] == 'sub'):
        if(old_payload['val'] == 'next_pege'):
            new_payload['page'] += 1
            output['message'] = 'Переход на следущую страницу.'
        elif(old_payload['val'] == 'previous_page'):
            new_payload['page'] -= 1
            output['message'] = 'Переход на предыдущую страницу.'
        elif(old_payload['val'] == 'return'):
            new_payload = old_payload['prnt']
            del new_payload['val']
            output['message'] = 'Главное меню.'
        else:
            new_payload['title'] = 'events'
            new_payload['page'] = 0
            new_payload['prnt'] = old_payload.copy()
            output['message'] = 'Выбор конкретного события.'
    elif(old_payload['title'] == 'events'):
        if(old_payload['val'] == 'next_page'):
            new_payload['page'] += 1
            output['message'] = 'Следующая страница.'
        elif(old_payload['val'] == 'previous_page'):
            new_payload['page'] -= 1
            output['message'] = 'Предыдущая страница'
        elif(old_payload['val'] == 'return'):
            new_payload = old_payload['prnt']
            del new_payload['val']
            output['message'] = 'Выбор категории.'
        else:
            new_payload['title'] = 'days'
            new_payload['page'] = 0
            new_payload['prnt'] = old_payload.copy()
            output['message'] = 'Выберете количество дней, за которое хотите получить оповещание.'
    elif(old_payload['title'] == 'days'):
        if(old_payload['val'] == 'next_pege'):
            new_payload['page'] += 1
            output['message'] = 'Следующая страница.'
        elif(old_payload['val'] == 'previous_page'):
            new_payload['page'] -= 1
            output['message'] = 'Предыдущая страница'
        elif(old_payload['val'] == 'return'):
            new_payload = old_payload['prnt']
            del new_payload['val']
            output['message'] = 'Выбор события.'
        else:
            new_payload = old_payload.copy()
            del new_payload['val']

            event_type = new_payload['prnt']['val']
            event_time_before = old_payload['val']
            user['wish_list'].append({'event_type': event_type, 'event_time_before': event_time_before})
            output['update_wish_list'] = (event_type, event_time_before)
            output['message'] = 'Добавлена подписка на %s за %d дней до события' % (old_payload['prnt']['prnt']['val'], event_time_before)
    elif(old_payload['title'] == 'unsub'): #TODO
        if(old_payload['val'] == 'next_pege'):
            new_payload['page'] += 1
            output['message'] = 'Следующая страница.'
        elif(old_payload['val'] == 'previous_page'):
            new_payload['page'] -= 1
            output['message'] = 'Предыдущая страница.'
        elif(old_payload['val'] == 'return'):
            new_payload = old_payload['prnt']
            del new_payload['val']
            output['message'] = 'Главное меню.'
        else:
            new_payload['title'] = 'sub'
            new_payload['page'] = 0
            new_payload['prnt'] = old_payload.copy()
    elif(old_payload['title'] == 'alert_time'):
        if(old_payload['val'] == 'return'):
            new_payload = old_payload['prnt']
            output['message'] = 'Главное меню'
        else:
            output['update_alert_time'] = old_payload['val']
            user['alert_time'] = old_payload['val']
            output['message'] = 'Время опевещаний установлено на %d:00.' % old_payload['val']
    elif(old_payload['title'] == 'adr_change'):
        if(old_payload['val'] == 'return'):
            new_payload = old_payload['prnt']
            output['message'] = 'Главное меню.'

    keyboard = VkKeyboard(one_time=False)

    #  Определение содержания основных кнопок
    if  (new_payload['title'] == 'main'):
        buttons = [
            ['sub', 'Меню подписок'],
            ['alert_time', 'Меню выбора времени оповещания'],
            ['unsub', 'Меню управления подписками'],
            ['adr_change', 'Меню смены адреса']
        ]
    elif(new_payload['title'] == 'sub'):
        buttons = list(data_set.keys())
    elif(new_payload['title'] == 'events'):
        buttons = data_set[new_payload['prnt']['val']]
    elif(new_payload['title'] == 'days'):
        possible_days = {1, 2, 3, 5, 7}
        if(old_payload['title'] == 'days'):
            event_type = old_payload['prnt']['val']
        elif(old_payload['title'] == 'events'):
            event_type = old_payload['val']
        selected_days = set(
            map(
                lambda a: a['event_time_before'],
                filter(
                    lambda b: b['event_type'] == event_type,
                    user['wish_list']
                )
            )
        )
        buttons = list(possible_days - selected_days)
    elif(new_payload['title'] == 'unsub'): #TODO
        pass
    elif(new_payload['title'] == 'alert_time'):
        buttons = [[i * 4 + j for j in range(4)] for i in range(6)]
    elif(new_payload['title'] == 'adr_change'): # TODO
        buttons = []

    # Если нужны странички
    left_arrow = False
    right_arrow = False
    if(new_payload['title'] != 'adr_change' and len(buttons) > 9):
        pages_list = get_pages(buttons, 8)
        page = new_payload['page']
        if(page > 0):
            left_arrow = True
        if(page < len(pages_list) - 1):
            right_arrow = True
        buttons = pages_list[page]

    # Создание основных кнопок
    if(new_payload['title'] == 'alert_time'):
        for line in buttons:
            for button in line:
                button_payload = new_payload.copy()
                button_payload.update({'val': button})
                button_payload = '{\"button\": \"%s\"}' % str(button_payload)
                if(user['alert_time'] == button):
                    color = VkKeyboardColor.POSITIVE
                else:
                    color = VkKeyboardColor.DEFAULT
                keyboard.add_button(label=f"{button}:00", payload=button_payload, color=color)
            keyboard.add_line()
    elif(len(buttons) and type(buttons[0]) == type([])):
        for val, label in buttons:
            button_payload = new_payload.copy()
            button_payload.update({'val': val})
            button_payload = '{\"button\": \"%s\"}' % str(button_payload)
            keyboard.add_button(label=label, payload=button_payload)
            if not(new_payload['title'] == 'main' and [val, label] == buttons[-1]):
                keyboard.add_line()
    elif(len(buttons)):
        for button in buttons:
            button_payload = new_payload.copy()
            button_payload.update({'val': button})
            button_payload = '{\"button\": \"%s\"}' % str(button_payload)
            keyboard.add_button(label=button, payload=button_payload)
            keyboard.add_line()

    # Создание стрелок
    if(left_arrow):
        arrow_payload = new_payload.copy()
        arrow_payload['val'] = 'previous_page'
        arrow_payload = '{\"button\": \"%s\"}' % str(arrow_payload)
        keyboard.add_button(label= '←', payload=arrow_payload)
    if(right_arrow):
        arrow_payload = new_payload.copy()
        arrow_payload['val'] = 'next_page'
        arrow_payload = '{\"button\": \"%s\"}' % str(arrow_payload)
        keyboard.add_button(label= '→', payload=arrow_payload)
    if(left_arrow or right_arrow):
        keyboard.add_line()

    # Создние кнопки Назад
    if(new_payload['title'] != 'main'):
        return_payload = new_payload.copy()
        return_payload.update({'val': 'return'})
        return_payload = '{\"button\": \"%s\"}' % str(return_payload)
        keyboard.add_button(label='Назад', payload=return_payload)

    output['keyboard'] = keyboard.get_keyboard()

    return output


def answer_bot(vk, db):
    longpoll = VkLongPoll(vk)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user = db.find_by_user_id(event.user_id)
            if(user is None):
                db.insert_one({'user_id': event.user_id})
                user = db.find_by_user_id(event.user_id)

            text = event.text
            print(text)
            payload = {}
            if(event.extra_values.get('payload') is not None):
                payload = json.loads(event.extra_values['payload'])
            answer = {'random_id': randint(0, 2**31), 'user_id': event.user_id, 'message': 'Команда не определена'}

            if(text.lower() == 'debug restart'):
                db.users.remove({'user_id': user['user_id']})
                answer['message'] = 'Акаунт сброшен'

            # Нажал кнопку "Начать"
            elif(text.lower() in ['начать', 'start'] and user['chat_stage'] == 'address_waiting'):
                message = """Добро пожаловать в Gradinformer
                Я могу сообщить тебе о том, что происходит в твоем городе.
                Например об отключении воды в твоем доме или мероприятии недалеко от тебя.
                
                Для регистрации напиши свой адрес. 
                При желании можно не указывать дом, тогда бедет сообщено об отключении на улице."""
                message = message.replace(' '*16, '')
                answer['message'] =  message

            # Ввел адрес
            elif(user['chat_stage'] == 'address_waiting'):
                geodata = str_to_geo_data(text)
                if(len(geodata)):
                    for key in geodata[0]:
                        db.update(user, key, geodata[0][key])
                    db.update(user, 'chat_stage', 'menu')

                    answer.update(menu(user))
                    message = f"""Установлен адрес {geodata[0]['full_address']}.
                    Изменить или уточнить его можно в Меню смены адреса."""
                    message = message.replace(' '*20, '')
                    answer['message'] = message
                else:
                    answer['message'] = 'Адрес не опознан, попробуйте еще раз'
            
            #Нажал на кнопку
            elif(payload.get('button') != None):
                menu_output = menu(user, payload['button'])
                if(menu_output.get('keyboard')):
                    answer['keyboard'] = menu_output['keyboard']
                if(menu_output.get('message')):
                    answer['message'] = menu_output['message']
                if(menu_output.get('update_alert_time')):
                    db.update(user, 'alert_time', menu_output['update_alert_time'])
                if(menu_output.get('update_wish_list')):
                    db.add_in_wish_list(user, *menu_output['update_wish_list'])
                if(menu_output.get('waiting_adress')):
                    db.update(user, 'chat_stage', 'address_waiting')

            else:
                answer['message'] = 'Команда не определена'

            vk.method('messages.send', answer)

def alert_bot(vk, db):
    pass 

if __name__ == "__main__":
    vk = vk_api.VkApi(token=vk_api_key)
    db = Database()

    answer_bot_thread = Thread(target=answer_bot, args=(vk, db,))
    alert_bot_tread   = Thread(target=alert_bot,  args=(vk, db,))
    
    answer_bot_thread.start()
    alert_bot_tread.start()
