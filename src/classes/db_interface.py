import pymongo
import os
from bson import ObjectId
class db_interface:
    def __init__(self):
        """database_url = os.environ["DATABASE_URL"]
        db_name = os.environ["DB_NAME"]
        collection_name = os.environ["COLLECTION_NAME"]"""
        #self.key_list = {'','',''}

        self.client = pymongo.MongoClient("mongodb://127.0.0.1:27017/") # connection to MongoDB
        self.database = self.client["publications-service"]  # select MongoDB's database
        self.collection = self.database["publications"] # select database's Collection

    def insert_one_publication(self, publication: dict) -> None:
        #pub_keys = publication.keys()      #Check dict validity
        #for key in self.key_list:
        #   if key is not in pub_keys:
        #       return Exception
        #else:
        self.collection.insert_one(publication)

    def delete_one_publication(self, publication_id: str) -> None:
        self.collection.delete_one({'_id': ObjectId(publication_id)})

    def delete_one_comment(self, comment_id: str, publication_id: str = '') -> None:
        if publication_id: # If there is a publication id to help the query
            self.collection.find_one_and_update(
                {"_id": ObjectId(publication_id)},
                {
                    "$pull":{
                        "comment":{
                            "_id": ObjectId(comment_id)
                        }
                    }
                }
            )
        else: # If there isn't :(
            self.collection.find_one_and_update(
                {},
                {
                    "$pull": {
                        "comment": {
                            "_id": ObjectId(comment_id)
                        }
                    }
                }
            )
