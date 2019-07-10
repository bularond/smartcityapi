#!/usr/bin/python
# -*- coding: utf-8 -*-
import pymongo as mdb
from datetime import datetime

class Database:
    def __init__(self):
        self.client = mdb.MongoClient('gradintegra.com', 27017)
        self.db = self.client['local']
        self.events = self.db['Events']
    
    def close(self):
        self.client.close()

    def load_data(self, data):
        if(len(data)):
            self.events.insert_many(data)

    def delete_old_than_date(self, date):
        self.events.remove({'end': {'$lt': date}})

if __name__ == "__main__":
    pass
