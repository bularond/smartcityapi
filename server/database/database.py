import pymongo as mdb
from datetime import datetime

class Database:
    def __init__(self):
        self.client = mdb.MongoClient('gradintegra.com', 27017)
        self.db = self.client['local']
        self.dhu = self.db['DHU']
    
    def close(self):
        self.client.close()

    def load_engergy_data(self, data):
        if(len(data)):
            self.dhu.insert_many(data)

    def delete_old_data(self):
        self.dhu.remove({'end': {'$lt': datetime.today()}})