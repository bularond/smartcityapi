import pymongo as mdb
from datetime import datetime

class Database:
    def __init__(self):
        self.client = mdb.MongoClient('gradintegra.com', 27017)
        self.db = self.client['local']
        self.dhu = self.db['DHU']
        self.user = self.db['User']
    
    def close(self):
        self.client.close()

    def load_engergy_data(self, data):
        if(len(data)):
            self.dhu.insert_many(data)

    def delete_old_data(self):
        self.dhu.remove({'end': {'$lt': datetime.today()}})

    def get_information_on_day(self, day_delta):
        return self.dhu.find({'begin': {'$eq': datetime().today() + day_delta}})

    def get_users_match_data(self, data):
        match_users = []
        for i in data:
            if(i['home_number'] == 0):
                match_users.append(self.user.find({'street': i['street']}))
            else:
                match_users.append(self.user.find({'street': i['street'], 'home_number': i['home_number']}))
        return match_users
