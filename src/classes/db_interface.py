import pymongo
import os
class db_interface:
    def __init__(self):
        database_url = os.environ["DATABASE_URL"]
        db_name = os.environ["DB_NAME"]
        collection_name = os.environ["COLLECTION_NAME"]

        self.client = pymongo.MongoClient(database_url) # connection to MongoDB
        self.database = self.client[db_name]  # select MongoDB's database
        self.collection = self.database[collection_name] # select database's Collection

    def insert_publication(self, publication: dict) -> None:
        #if publication[''] and publication[''] # format check
        self.collection.insert_one(publication)