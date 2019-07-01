import smtp_mail
import pymongo

smtp_obj = smtp_mail.SMTP("no-repy@gradintegra.com", "|kko)8s2K(WT6u!m")        #Create smtp ojbect SMTP("login", "password")
client = pymongo.MongoClient("gradintegra.com", 27017)

list_of_DHU = list(client.local.DHU.find())
list_of_Users = list(client.local.Users.find())

message_list = []
for doc_DHU in list_of_DHU:
    for doc_User in list_of_Users:
        if doc_DHU["street"] == doc_User["street"] and doc_DHU["home_number"] == 0:
            doc_User["begin"] = doc_DHU["begin"]
            doc_User["end"] = doc_DHU["end"]
            doc_User["type"] = doc_DHU["type"]
            message_list.append(doc_User)
        elif doc_DHU["street"] == doc_User["street"] and doc_DHU["home_number"]==int(doc_User["home"]):
            doc_User["begin"] = doc_DHU["begin"]
            doc_User["end"] = doc_DHU["end"]
            doc_User["type"] = doc_DHU["type"]
            message_list.append(doc_User)


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



for man in message_list:
    if man["type"] == "energy":
        if man["begin"].day == man["end"].day and man["begin"].month == man["end"].month and man["begin"].year == man["end"].year:
            message = "Уважаемый " + man["FIO"] +"!\nХотим сообщить, что " + str(man["begin"].day) + " " + str(month[man["begin"].month]) + " на улице "+doc_User["street"] + " планируется отключение электричества."
            smtp_obj.send_message(man["mail"], message, "Отключение электроэнергии")
    elif man["type"] == "water":
        pass




#smtp_obj.send_message("djalil6789@gmail.com", "qweqwtrt", "wrtjj")              #Send message send_message("destination mail", "message0", "Subject")
