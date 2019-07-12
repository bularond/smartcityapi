#!/usr/bin/python
# -*- coding: utf-8 -*-
import pymongo as mdb
from datetime import datetime

class Database:
    def __init__(self):
        self.client = mdb.MongoClient('gradintegra.com', 27017)
        self.db = self.client['local']
        self.users = self.db['Users_mailer']
    
    def close(self):
        self.client.close()

    def get_cursor(self, request={}):
        return self.users.find(request)

if __name__ == "__main__":
    pass
