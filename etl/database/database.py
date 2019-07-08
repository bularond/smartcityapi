#!/usr/bin/python
# -*- coding: utf-8 -*-
import pymongo as mdb
from datetime import datetime

class Database:
    def __init__(self):
        self.client = mdb.MongoClient('gradintegra.com', 27017)
        self.db = self.client['local']
        self.dhu = self.db['DHU']
        self.user = self.db['Users']
    
    def close(self):
        self.client.close()

    def load_engergy_data(self, data):
        if(len(data)):
            self.dhu.insert_many(data)

    def delete_old_than_date(self, date):
        self.dhu.remove({'end': {'$lt': date}})

    def get_information_on_days(self, begin = datetime.today(), end = None):
        if(end == None):
            end = begin
        return list(self.dhu.find({'begin': {'$gte': begin, '$lte': end}}))

    def find_in_dhu(self, request_dict):
        return list(self.dhu.find(request_dict))

    def get_users_match_data(self, data):
        match_users = []
        for dhu_data in data:
            if(dhu_data['home_number'] == 0):
                temp_list = list(self.user.find({'street': dhu_data['street']}))
                for man_id in range(len(temp_list)):
                    temp_list[man_id].update(dhu_data)
                match_users += temp_list
            else:
                temp_list = list(self.user.find({'street': dhu_data['street'], 'home_number': dhu_data['home_number']}))
                for man_id in range(len(temp_list)):
                    temp_list[man_id].update(dhu_data)
                match_users += temp_list
        return match_users

if __name__ == "__main__":
    db = Database()
    data = db.find_in_dhu({})
    print(type(data))
    print(data[0])
