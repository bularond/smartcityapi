import mailer.smtp_mail
import pymongo



def send_messages(message_list):
    smtp_obj = smtp_mail.SMTP("no-repy@gradintegra.com", "|kko)8s2K(WT6u!m")        #Create smtp ojbect SMTP("login", "password")
    month = {
        1:"января",
        2:"февраля",
        3:"марта",
        4:"апреля",
        5:"мая",
        6:"июня",
        7:"июля",
        8:"августа",
        9:"сентября",
        10:"октября",
        11:"ноября",
        12:"декабря"
    }
    types = {
        "energy": "отключение электричества"
    }
    for man in message_list:
        message = f"""Уважаемый {man["FIO"]}!
\nХотим сообщить, что {str(man["begin"].day)} {str(month[man["begin"].month])} на улице {doc_User["street"]} планируется {types[man["type"]]}."""
        smtp_obj.send_message(man["mail"], message, "Отключение электроэнергии")




#smtp_obj.send_message("djalil6789@gmail.com", "qweqwtrt", "wrtjj")              #Send message send_message("destination mail", "message0", "Subject")
