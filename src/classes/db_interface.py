import pymongo

class db_interface:
    def __init__(self):
        self.client = pymongo.MongoClient('mongodb:http://mongo.db') # connection to MongoDB
        self.database = self.client['publication-service'] # select MongoDB's database
        self.collection = self.database['publications'] # select database's Collection

    def insert_publication(self, publication: dict) -> None:
        #if publication[''] and publication[''] # format check
        self.collection.insert_one(publication)