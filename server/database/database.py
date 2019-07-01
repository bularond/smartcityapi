import pymongo as mdb

def load_engergy_data(data):
    client = mdb.MongoClient('gradintegra.com', 27017)
    db = client['local']
    dhu = db['DHU']
    dhu.insert_many(data)


