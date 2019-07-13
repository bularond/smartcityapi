## -*- coding: utf-8 -*-
from flask import Flask, abort
from flask import request
import flask
import pymongo
from pymongo import GEO2D
import json
from bson import ObjectId
conn = pymongo.MongoClient("gradintegra.com", 27017)

app = Flask(__name__)


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
        "offset":request.args.get('offset', default = 1, type = int),
        "lat":request.args.get('lat', default = None, type = float),
        "lon":request.args.get('lon', default = None, type = float),
        "description":request.args.get('description', default = None, type = str),
        "street":request.args.get('street', default = None, type = str),
        "house":request.args.get('house', default = None, type = str),

    }
    deff_ev = []
    for arg in arguments:
        if arguments[arg] != None:
            if arg == "type":
                deff_ev.append({arg:arguments[arg]})
            elif arg == "begin":
                if arguments["end"] == None:
                    abort(400, "You need to set the end time")
                else:
                    try:
                        deff_ev.append({"$and":[{"begin":{"$gte":arguments["begin"], "$lte":arguments["end"]}}, {"end":{"$gte":arguments["begin"], "$lte":arguments["end"]}}]})
                    except:
                        pass
            elif arg == "end":
                if arguments["begin"] == None:
                    abort(400, "You need to set the begin time")
                else:
                    try:
                        deff_ev.append({"$and":[{"begin":{"$gte":arguments["begin"], "$lte":arguments["end"]}}, {"end":{"$gte":arguments["begin"], "$lte":arguments["end"]}}]})
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
            elif arg == "description":
                try:
                    deff_ev.append({arg: {"$regex": arguments[arg]}})
                except:
                    pass
    good_ev = {}
    print(deff_ev)
    for i in range(min(events.find({"$and":deff_ev}).count(), arguments["offset"])):
        good_ev[i] = (serial(events.find({"$and":deff_ev})[i]))
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

@app.route('/api/post_event', methods=['POST'])
def post_event():
    events = conn.local.Events
    arguments = {
        "type":request.args.get('type', default = None, type = str),
        "begin":request.args.get('begin', default = None, type = int),
        "end":request.args.get('end', default = None, type = int),
        "lat":request.args.get('lat', default = None, type = float),
        "lon":request.args.get('lon', default = None, type = float),
        "description":request.args.get('description', default = None, type = str),
        "street":request.args.get('street', default = "", type = str),
        "house":request.args.get('house', default = "", type = str),
        "text":request.args.get('text', default = "", type = str),
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
            elif arg == "description":
                abort(500, "Description is required")
            elif arg == "end":
                bad_end = arguments["begin"] + 24*3600
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
                "text":arguments["text"]
            }
        )
        return({"status":"OK"})
    except Exception as e:
        abort(200)

if __name__ == '__main__':
    app.run(host= '0.0.0.0', port = 1337)

