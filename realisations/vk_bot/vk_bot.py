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

def  gen_keyboard(exist):
    url = api_url + 'event_types'
    responde = requests.get(url)
    event_types = responde.json()
    event_types = list(event_types.values())
    event_types = list(filter(lambda event_type: event_type['type'] not in exist, event_types))

    keyboard = {
        "one_time": True,
        "buttons": []
    }
    for event_type in event_types:
        keyboard["buttons"].append(
            [{
                "action": {
                    "type": "text",
                    "label": event_type['title'],
                    "payload": '{"button": "%s"}' % event_type['type']
                }
            }]
        )
    keyboard["buttons"].append(
            [{
                "action": {
                    "type": "text",
                    "label": " Далее",
                    "payload": '{"button": "Далее"}'
                },
                "color": "primary"
            }]
        )
    return json.dumps(keyboard)

data_set = {
    'ЖКХ': [
        "Отключение воды",
        "Отключение электричества"
    ],
    'Мероприятия': [
        'Концерт',
        'День открытых дверей',
        'Пьесса'
    ]
}

def get_pages(lst, count):
    offset = 0
    pages = []
    while(offset < len(lst)):
        pages.append(lst[offset:offset+count])
        offset += count
    return pages


def add_in_wishlist(user, event_type, event_time_before):
    print(user['user_id'], event_type, event_time_before)


def menu(user, old_payload = None):
    if(old_payload == None):
        old_payload = '{"value": "return", "parent": {"menu_title": "main_menu", "page": 0, "value": ""}, "menu_title": "sub_menu", "page": 0}'
    else:
        old_payload = old_payload.replace("'", '"')

    old_payload = json.loads(old_payload)
    new_payload = {
        'menu_title': old_payload['menu_title'],
        'page': old_payload['page'],
        'parent': {}
    }

    # Реагирование на кнопку, определение новой клавиатуры
    if(old_payload['menu_title'] == 'main_menu'):
        if(old_payload['value'] == 'next_pege'):
            new_payload['page'] += 1
        elif(old_payload['value'] == 'previous_page'):
            new_payload['page'] -= 1
        elif(old_payload['value'] == 'next'):
            return None
        else:
            new_payload['menu_title'] = 'sub_menu'
            new_payload['page'] = 0
            new_payload['parent'] = old_payload.copy()
    elif(old_payload['menu_title'] == 'sub_menu'):
        if(old_payload['value'] == 'next_pege'):
            new_payload['page'] += 1
        elif(old_payload['value'] == 'previous_page'):
            new_payload['page'] -= 1
        elif(old_payload['value'] == 'return'):
            new_payload = old_payload['parent']
            del new_payload['value']
        else:
            new_payload['menu_title'] = 'days_menu'
            new_payload['page'] = 0
            new_payload['parent'] = old_payload.copy()
    elif(old_payload['menu_title'] == 'days_menu'):
        if(old_payload['value'] == 'next_pege'):
            new_payload['page'] += 1
        elif(old_payload['value'] == 'previous_page'):
            new_payload['page'] -= 1
        elif(old_payload['value'] == 'return'):
            new_payload = old_payload['parent']
            del new_payload['value']
        else:
            new_payload = old_payload.copy()
            del new_payload['value']
            add_in_wishlist(user, old_payload['parent']['value'], old_payload['value'])

    keyboard = VkKeyboard(one_time=False)

    #  Определение содержания кнопок
    if(new_payload['menu_title'] == 'main_menu'):
        buttons = list(data_set.keys())
    elif(new_payload['menu_title'] == 'sub_menu'):
        buttons = data_set[new_payload['parent']['value']]
    elif(new_payload['menu_title'] == 'days_menu'):
        buttons = [1, 2, 3, 5, 7]

    # Создание основных кнопок
    if(len(buttons) <= 9):
        for button in buttons:
            button_payload = new_payload.copy()
            button_payload.update({'value': button})
            button_payload = '{\"button\": \"%s\"}' % str(button_payload)
            keyboard.add_button(label=button, payload=button_payload)
            keyboard.add_line()
    else:
        pages_list = get_pages(buttons, 8)
        page = new_payload['page']
        for button in pages_list[page]:
            button_payload = new_payload.copy()
            button_payload.update({'value': button})
            button_payload = '{\"button\": \"%s\"}' % str(button_payload)
            keyboard.add_button(label=button, payload=button_payload)
            keyboard.add_line()
        # Создание стрелок
        if(page != 0):
            arrow_payload = new_payload.copy()
            arrow_payload['value'] = 'previous_page'
            arrow_payload = '{\"button\": \"%s\"}' % str(arrow_payload)
            keyboard.add_button(label= '←', payload=arrow_payload)
        if(page != len(pages_list) - 1):
            arrow_payload = new_payload.copy()
            arrow_payload['value'] = 'next_page'
            arrow_payload = '{\"button\": \"%s\"}' % str(arrow_payload)
            keyboard.add_button(label= '→', payload=arrow_payload)
        keyboard.add_line()
    
    # Создние кнопки Далее/назад
    if(new_payload['menu_title'] == 'main_menu'):
        return_payload = new_payload.copy()
        return_payload.update({'value': 'next'})
        return_payload = '{\"button\": \"%s\"}' % str(return_payload)
        keyboard.add_button(label='Далее', payload=return_payload)
    else:
        return_payload = new_payload.copy()
        return_payload.update({'value': 'return'})
        return_payload = '{\"button\": \"%s\"}' % str(return_payload)
        keyboard.add_button(label='Назад', payload=return_payload)
    
    return keyboard.get_keyboard()


def answer_bot(vk, db):
    longpoll = VkLongPoll(vk)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user = db.find_by_user_id(event.user_id)
            if(user is None):
                db.insert_one({'user_id': event.user_id})
                user = db.find_by_user_id(event.user_id)

            text = event.text
            payload = {}

            if(event.extra_values.get('payload') is not None):
                payload = json.loads(event.extra_values['payload'])

            answer = {'random_id': randint(0, 2**31), 'user_id': event.user_id}

            
            # Нажал кнопку "Начать"
            if(text.lower() == 'начать' and user['chat_stage'] == 'registration'):
                message = """Добро пожаловать в Gradinformer
                Я могу сообщить тебе о том, что происходит в твоем городе.
                Например об отключении воды в твоем доме или мероприятии недалеко от тебя.
                
                Для регистрации напиши свой адрес. 
                При желании можно не указывать дом, тогда бедет сообщено об отключении на улице."""
                answer['message'] =  message

            # Ввел адрес
            elif(user['chat_stage'] == 'registration'):
                string = text.lower().replace('адрес', '')
                geodata = str_to_geo_data(string)
                if(len(geodata)):
                    for key in geodata[0]:
                        db.update(user, key, geodata[0][key])
                    db.update(user, 'chat_stage', 'pushing')

                    answer['message'] = f"""Установлен адрес {geodata[0]['text']}.
                    Чтобы его изменить напишите "Изменить адрес".

                    Далее выберете события, на которые хотите подписаться
                    """

                    answer['keyboard'] = menu(user)
                    print(answer['keyboard'])
                else:
                    answer['message'] = 'Адрес не опознан, попробуйте еще раз'

            elif(payload.get('button') != None):
                answer['keyboard'] = menu(user, payload['button'])
                answer['message'] = '1'
            
            else:
                answer['message'] = '2'

            vk.method('messages.send', answer)

if __name__ == "__main__":
    vk = vk_api.VkApi(token=vk_api_key)
    db = Database()

    answer_bot_thread = Thread(target=answer_bot, args=(vk, db,))
    answer_bot_thread.start()
