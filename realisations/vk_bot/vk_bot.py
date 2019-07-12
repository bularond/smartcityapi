import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from settings import vk_api_key, api_url
from threading import Thread
import requests
import json

keypad = {
    "one_time": False,
    "buttons": [
        [
            {
                "action": {
                    "type": "location",
                    "payload": "{\"button\": \"1\"}"
                }
            }
        ],
        [
            {
                "action": {
                    "type": "open_app",
                    "app_id": 6979558,
                    "owner_id": -181108510,
                    "hash": "sendKeyboard",
                    "label": "Отправить клавиатуру"
                }
            }
        ],
        [
            {
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"1\"}",
                    "label": "Negative"
                },
                "color": "negative"
            },
            {
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"2\"}",
                    "label": "Positive"
                },
                "color": "positive"
            },
            {
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"2\"}",
                    "label": "Primary"
                },
                "color": "primary"
            },
            {
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"2\"}",
                    "label": "Secondary"
                },
                "color": "secondary"
            }
        ]
    ]
}


def gen_welcome_message():
    url = api_url + 'enent_list'
    responde = requests.get(url)
    event_list = responde.json()

    welcome_message = """
        Добро пожаловать в Gradinformer.

        Вы можете подписаться на события, происходящие в вашем городе.
        Для этого выберете интересующие вас котегории.
        """
    
    keyboard = {
        "one_time": False,
        "buttons": []
    }

    for 


def answer_bot(vk, welcome_message):
    longpoll = VkLongPoll(vk)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            message = event.text


if __name__ == "__main__":
    vk = vk_api.VkApi(token=vk_api_key)
    #answer_bot_thread = Thread(target=answer_bot, args=(vk,))
    keypad = json.dumps(keypad)
    vk.method('messages.send', {'user_id': 160229003, 'random_id': 0, 'message': '2', 'keyboard': keypad})
