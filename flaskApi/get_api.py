## -*- coding: utf-8 -*-
from flask import Flask, abort
from flask import request
from smtp_mail import SMTP
from flask_cors import CORS
from pymongo import GEO2D
from bson import ObjectId
import hashlib as hl
import flask
import pymongo
import string
import random
import json

conn = pymongo.MongoClient("gradintegra.com", 27017)

app = Flask(__name__)
CORS(app)


sender = SMTP("no-repy@gradintegra.com", "|kko)8s2K(WT6u!m")


accept_form = "Здравствуйте.\nНа наш сервер пришел запрос о регистрации нового пользователя под ником {}\nПерейдите по ссылке {} для подтверждеия своего аккаунта.\nЕслы Вы не регистрировали аккаунт на сервисе GradInformer проигнорируйте данное сообщение."


def serial(dct):
    for k in dct:
        if isinstance(dct[k], ObjectId):
            dct[k] = str(dct[k])
    return dct

@app.route('/api/event', methods=['GET'])
def get_event():
    events = conn.local.Events
    arguments = {
        "type":request.args.get('type', default = None, type = str),
        "begin":request.args.get('begin', default = None, type = int),
        "end":request.args.get('end', default = None, type = int),
        "count":request.args.get('count', default = 20, type = int),
        "offset":request.args.get('offset', default = 0, type = int),
        "lat":request.args.get('lat', default = None, type = float),
        "lon":request.args.get('lon', default = None, type = float),
        "description":request.args.get('description', default = None, type = str),
        "street":request.args.get('street', default = None, type = str),
        "house":request.args.get('house', default = None, type = str),
        "contact":request.args.get('contact', default = None, type = str),
        "_id":request.args.get('_id', default = None, type = str),

    }
    deff_ev = []
    if arguments["_id"] != None:
        return events.find({"_id":ObjectId(arguments["_id"])})[0]
    for arg in arguments:
        if arguments[arg] != None:
            if arg == "type":
                deff_ev.append({arg:arguments[arg]})
            elif arg == "begin":
                if arguments["end"] == None:
                    abort(400, "You need to set the end time")
                else:
                    try:
                        deff_ev.append({"begin":{"$gte":arguments["begin"], "$lte":arguments["end"]}})
                    except:
                        pass
            elif arg == "end":
                if arguments["begin"] == None:
                    abort(400, "You need to set the begin time")
                else:
                    try:
                        deff_ev.append({"begin":{"$gte":arguments["begin"], "$lte":arguments["end"]}})
                    except:
                        pass
            elif arg == "lat":
                if arguments["lon"] == None:
                    abort(400, "You need to set the longitude")
                else:
                    try:
                        deff_ev.append({"point" : {
                            "type" : "Point",
                            "coordinates" : [
                                arguments["lon"],
                                arguments["lat"]
                            ]
                        }})
                    except:
                        pass
            elif arg == "lon":
                if arguments["lat"] == None:
                    abort(400, "You need to set the latitude")
                else:
                    try:
                        deff_ev.append({"point" : {
                            "type" : "Point",
                            "coordinates" : [
                                arguments["lon"],
                                arguments["lat"]
                            ]
                        }})
                    except:
                        pass
            elif arg == "street":
                try:
                    deff_ev.append({arg:arguments[arg]})
                except:
                    pass
            elif arg == "house":
                try:
                    deff_ev.append({arg:arguments[arg]})
                except:
                    pass
            elif arg == "contact":
                try:
                    deff_ev.append({arg:arguments[arg]})
                except:
                    pass
            elif arg == "description":
                try:
                    deff_ev.append({arg: {"$regex": arguments[arg]}})
                except:
                    pass
    good_ev = {}
    if len(deff_ev) == 0:
        for i in range(min(events.find({}).count(), arguments["count"])):
            good_ev[i] = (serial(events.find({})[i]))
            print(good_ev[i])
    elif len(deff_ev) == 1:
        print(deff_ev)
        for i in range(min(events.find(deff_ev[0]).count(), arguments["count"])):
            good_ev[i] = (serial(events.find(deff_ev[0])[i]))
            print(good_ev[i])
    else:
        for i in range(min(events.find({"$and":deff_ev}).count(), arguments["count"])):
            good_ev[i] = (serial(events.find({"$and":deff_ev})[i]))
            print(good_ev[i])
    return good_ev

@app.route('/api/event_types', methods=['GET'])
def get_event_types():
    event_types = conn.local.Event_Types
    return_types = {}
    c = 0
    for type in event_types.find({}):
        return_types[c] = serial(type)
        c = c+1
    print(return_types)
    return return_types

@app.route('/api/login', methods=['POST'])
def login():
    auth_data = request.json
    users = conn.local.Users_writers
    password = hl.md5(auth_data["password"].encode()).hexdigest()
    login = auth_data["login"]
    if users.find({"login":login, "password":password}).count() > 0:
        return {"status":"OK", "api_key":users.find({"login":login, "password":password})[0]["api_key"]}
    else:
        return {"status": "BAD AUTH"}

@app.route('/api/verification', methods=['GET'])
def verification():
    url = request.args.get('url', default = None, type = str)
    users = conn.local.Users_writers
    na_users = conn.local.NA_Users_writers
    if url == None:
        print(na_users.find({"auth_url":url}).count())
        abort(500, "You need sets the correct url")
    else:
        if na_users.find({"auth_url":url}).count() == 1:
            new_db = serial(na_users.find({"auth_url":url})[0])
            new_db.pop("_id", None)
            new_db.pop("auth_url", None)
            new_db["api_key"] = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
            na_users.delete_one({"auth_url":url})
            users.insert_one(new_db)
        else:
            abort(500, "You need set the correct url")

    return {"status": "OK"}

@app.route('/api/registration', methods=['POST'])
def registrantion():
    users = conn.local.NA_Users_writers
    exist_users = conn.local.Users_writers
    reg_data = request.json
    log = reg_data["login"]
    mail = reg_data["email"]
    print(exist_users.find({"login":login, "email":mail}))
    if users.find({"login":login, "email":mail}).count() > 0 or exist_users.find({"login":login, "email":mail}).count()>0:
        print("BABABBABAAB")
        return {"status":"User with this login or email is exist"}
    else:
        enc_pass = hl.md5(reg_data["password"].encode()).hexdigest()
        url = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
        users.insert_one({"auth_url":url, "login":log, "email":mail, "password":enc_pass})
        sender.send_message(mail, accept_form.format(log, "localhost:1337/api/verification?url={}".format(url)), "GradInformer")
        print(reg_data)
        return reg_data

@app.route('/api/put_event', methods=['PUT'])
def put_event():
    content = request.json
    events = conn.local.Events
    return {"status":"OK"}


@app.route('/api/set_event', methods=['POST'])
def post_event():
    content = request.json
    print(content)
    events = conn.local.Events
    users = conn.local.Users_writers

    arguments = {
        "type":content.get("type"),
        "begin":content.get("begin"),
        "end":content.get("end"),
        "lat":float(content.get("lat")),
        "lon":float(content.get("lon")),
        "description":content.get("description"),
        "street":content.get("street"),
        "house":content.get("house"),
        "full_address":content.get("full_address"),
        "city":content.get("city"),
        "token":content.get("token"),
    }

    bad_end = arguments["end"]
    for arg in arguments:
        if arguments[arg] == None:
            if arg == "type":
                abort(500, "Type is required")
            elif arg == "begin":
                abort(500, "Type is required")
            elif arg == "lat":
                abort(500, "Latitude is required")
            elif arg == "lon":
                abort(500, "Longitude is required")
            elif arg == "city":
                abort(500, "City is required")
            elif arg == "description":
                abort(500, "Description is required")
            elif arg == "end":
                bad_end = arguments["begin"] + 24*3600
            elif arg =="token":
                abort(500, "Api key is required")
    if users.find({"api_key":arguments["token"]}).count() == 0:
        abort(500, "Invalid API key")
    try:
        events.insert_one(
            {
                "type":arguments["type"],
                "begin":arguments["begin"],
                "end":bad_end,
                "lat":arguments["lat"],
                "lon":arguments["lon"],
                "description":arguments["description"],
                "street":arguments["street"],
                "house":arguments["house"],
                "full_address":arguments["full_address"],
                "city":arguments["city"],

            }
        )
        return({"status":"OK"})

    except Exception as e:
        abort(200)

if __name__ == '__main__':
    app.run(host= '0.0.0.0', port = 1337)
