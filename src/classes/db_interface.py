import pymongo
from pymongo.collection import ReturnDocument
import os
from pprint import pprint
from bson import ObjectId
class db_interface:
    def __init__(self):
        """database_url = os.environ["DATABASE_URL"]    #get every values of env
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
        print("\nPublication:")
        pprint(publication)
        print("inserted in database")

    def add_one_comment(self, comment: dict, publication_id: str) -> None:
        #self.collection.find_one_and_update()
        pass

    def add_one_reply(self, reply: dict, publication_id: str, comment_id: str) -> None:
        pass

    def delete_one_publication(self, publication_id: str) -> None: #NOT TESTED
        removed_publication = self.collection.find_one_and_delete({'_id': ObjectId(publication_id)})
        pprint("\nPublication:\n", removed_publication,"\n removed from the database")
    
    def delete_user_publications(self, user_name: str) -> None:  # NOT TESTED
        log = self.collection.delete_many({'user_name': user_name})
        print(f"\n{log.deleted_count} publications of {user_name} removed")

    def get_one_publication(self, publication_id: str) -> dict:
        publication = self.collection.find_one({"_id": ObjectId(publication_id)})
        print("\nPublication:")
        pprint(publication)
        print("returned")
        return publication

    def get_user_publications(self, user_name: str) -> [dict] or []:#NOT TESTED
        cursor = self.collection.find({'user_name': user_name})
        publications = []

        for publication in cursor:
            publications.append(publication)
        pprint(f"Publications:\n{publications}\nreturned")
        return publications

    def delete_one_comment(self, comment_id: str, publication_id: str) -> None: #NOT TESTED
        updated_publication = self.collection.find_one_and_update(
            {"_id": ObjectId(publication_id)},
            {
                "$pull":{
                    "comments":{
                        "_id": ObjectId(comment_id)
                    }
                }
            },
            return_document=ReturnDocument.AFTER
        )
        pprint(f"Publication:\n{updated_publication}\nsuccessfully updated")

    def delete_one_reply(self, reply_id: str, publication_id: str) -> None:#NOT TESTED
        # Can be improved by adding a comment_id to support the query
        updated_publication = self.collection.find_one_and_update(
            {"_id": ObjectId(publication_id)},
            {
                "$pull": {
                    "comments.replies": {
                        "_id": ObjectId(reply_id)
                    }
                }
            },
            return_document=ReturnDocument.AFTER
        )
        pprint(f"Publication:\n{updated_publication}\nsuccessfully updated")
