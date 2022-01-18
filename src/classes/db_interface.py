import pymongo
import os
class db_interface:
    def __init__(self):
        """database_url = os.environ["DATABASE_URL"]
        db_name = os.environ["DB_NAME"]
        collection_name = os.environ["COLLECTION_NAME"]"""

        self.client = pymongo.MongoClient("mongodb://127.0.0.1:27017/") # connection to MongoDB
        self.database = self.client["publications-service"]  # select MongoDB's database
        self.collection = self.database["publications"] # select database's Collection

    def insert_publication(self, publication: dict) -> None:
        #if publication[''] and publication[''] # format check
        self.collection.insert_one(publication)