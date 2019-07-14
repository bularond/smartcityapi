#!/usr/bin/python
# -*- coding: utf-8 -*-
import pymongo as mdb
from datetime import datetime

class Database:
    def __init__(self):
        self.client = mdb.MongoClient('gradintegra.com', 27017)
        self.db = self.client['local']
        self.users = self.db['Users_vk']
    
    def close(self):
        self.client.close()

    def find_by_user_id(self, user_id):
        user = list(self.users.find({"user_id": user_id}))
        if(len(user)):
            return user[0]
        else:
            return None

    def insert_one(self, user):
        user_tuple = {
            "user_id" : 0,
            "street" : "",
            "house" : "",
            "wish_list" : [],
            "house_geopos" : {},
            "chat_stage": 'registration'
        }
        user_tuple.update(user)
        self.users.insert(user_tuple)

    def update(self, users, key, value):
        self.users.update(
            {
                'user_id': users['user_id']
            }, 
            {
                '$set': {
                    key: value
                }
            }
        )
    
    def add_in_wish_list(self, user, event_type, event_time_before):
        self.users.update(
            {
                'user_id': user['user_id']
            }, 
            {
                '$push': {
                    'wish_list': {
                        'event_type': event_type,
                        'event_time_before': event_time_before
                    }
                }
            }
        )

if __name__ == "__main__":
    pass
