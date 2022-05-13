import pymongo
from pymongo.collection import ReturnDocument
import os
from pprint import pprint
from bson import ObjectId
import datetime
import gridfs


class DBInterface:

    def __init__(self):
        if os.environ["DEPLOYMENT_MODE"] == "PROD":
            database_url = os.environ["DATABASE_URL"]  # get every value of env
            db_name = os.environ["DB_NAME"]
            collection_name = os.environ["COLLECTION_NAME"]

            self.client = pymongo.MongoClient(database_url)  # connection to MongoDB
            self.database = self.client[db_name]  # select MongoDB's database
            self.collection = self.database[collection_name]  # select database's Collection

            print("INFO: Deployment in production mode.")

        elif os.environ["DEPLOYMENT_MODE"] == "DEBUG":
            self.client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")  # connection to MongoDB
            self.database = self.client["publications-service"]  # select MongoDB's database
            self.collection = self.database["publications"]  # select database's Collection

            print("INFO: Deployment in debug mode.")

        else:
            print("ERROR: Bad deployment mode.")
            exit(1)

        self.fs = gridfs.GridFS(self.database)  # Set up GridFS for the database

    def insert_one_publication(self, publication: dict) -> str:
        result = self.collection.insert_one(publication)
        print(f"Publication {result.inserted_id} inserted in database")
        return str(result.inserted_id)

    def add_one_comment(self, comment: dict, publication_id: str) -> None:
        pass

    def add_one_reply(self, reply: dict, publication_id: str, comment_id: str) -> None:
        pass

    def delete_one_publication(self, publication_id: str) -> dict:
        removed_publication = self.collection.find_one_and_delete({'_id': ObjectId(publication_id)})
        pprint("\nPublication:")
        pprint(removed_publication)
        pprint("removed from the database")
        return removed_publication

    def delete_user_publications(self, user_name: str) -> pymongo.results.DeleteResult:
        log = self.collection.delete_many({'user_name': user_name})
        print(f"\n{log.deleted_count} publications of {user_name} removed")
        return log

    def get_one_publication(self, publication_id: str) -> dict or None:
        publication = self.collection.find_one({"_id": ObjectId(publication_id)})
        if publication is not None:
            print("Publication " + str(publication["_id"]) + " returned.")
        return publication

    def get_user_publications(self, user_name: str) -> list[dict] or list:
        cursor = self.collection.find({'user_name': user_name})
        publications = []

        for publication in cursor:
            publications.append(publication)
        print(f"{len(publications)} publications returned for {user_name}")
        return publications

    def delete_one_comment(self, comment_id: str, publication_id: str) -> bool:
        updated_publication = self.collection.find_one_and_update(
            {
                "_id": ObjectId(publication_id),
                "comments._id": ObjectId(comment_id)
            },
            {
                "$pull": {
                    "comments": {
                        "_id": ObjectId(comment_id)
                    }
                }
            },
            return_document=ReturnDocument.AFTER
        )
        if updated_publication is None:
            return False
        else:
            pprint(f"Publication {publication_id} successfully updated")
            return True

    def delete_one_reply(self, reply_id: str, comment_id: str, publication_id: str) -> bool:
        updated_publication = self.collection.find_one_and_update(
            {
                "_id": ObjectId(publication_id),
                "comments._id": ObjectId(comment_id),
                "comments.replies._id": ObjectId(reply_id)
            },
            {
                "$pull": {
                    "comments.$.replies": {
                        "_id": ObjectId(reply_id)
                    }
                }
            },
            return_document=ReturnDocument.AFTER
        )
        if updated_publication is None:
            return False
        else:
            pprint(f"Publication {publication_id} successfully updated")
            return True

    def upvote_one_publication(self, publication_id) -> bool:
        updated_pub = self.collection.find_one_and_update(
            {"_id": ObjectId(publication_id)},
            {
                "$inc": {
                    "likes_count": 1
                }
            }
        )
        if updated_pub is None:
            return False
        else:
            print(f'Publication \'{publication_id}\' got 1 like.')
            return True

    def upvote_one_comment(self, publication_id: str, comment_id: str):
        updated_pub = self.collection.find_one_and_update(
            {
                "_id": ObjectId(publication_id),
                "comments._id": ObjectId(comment_id)
            },
            {
                "$inc": {
                    "comments.$.likes_count": 1
                }
            }
        )
        if updated_pub is None:
            return False
        else:
            print(f'Comment \'{comment_id}\' got a like.')
            return True

    # FIXME
    def upvote_one_reply(self, publication_id: str, comment_id: str, reply_id: str):
        updated_pub = self.collection.find_one_and_update(
            {
                "_id": ObjectId(publication_id),
                "comments._id": ObjectId(comment_id),
                "comments.replies._id": ObjectId(reply_id)
            },
            {
                "$inc": {
                    "replies.$.likes_count": 1
                }
            },
            return_document=ReturnDocument.AFTER
        )
        print(updated_pub)
        if updated_pub is None:
            return False
        else:
            print(f'Reply \'{reply_id}\' got a like.')
            return True

    def insert_one_comment(self, publication_id: str, comment: dict) -> str:
        result = self.collection.find_one_and_update(
            {
                "_id": ObjectId(publication_id)
            },
            {
                "$addToSet": {
                    "comments": comment
                }
            },
            return_document=ReturnDocument.AFTER
        )
        result_id = result["comments"][-1]["_id"]
        print(f"Comment with id '{result_id}' by '{result['comments'][-1]['user']}' inserted in DB")
        return result_id

    def insert_one_reply(self, publication_id: str, comment_id: str, reply: dict) -> str:
        new_id = ObjectId()
        reply["_id"] = new_id
        result = self.collection.find_one_and_update(
            {
                "_id": ObjectId(publication_id),
                "comments._id": ObjectId(comment_id)
            },
            {
                "$addToSet": {
                    "comments.$.replies": reply
                }
            },
            return_document=ReturnDocument.AFTER
        )
        #result_id = result["replies"][-1]["_id"]
        print(
            f"Reply with id '{new_id}' by '{reply['user']}' inserted in DB")
        return str(new_id)

    def downvote_one_publication(self, publication_id: str) -> bool:
        updated_pub = self.collection.find_one_and_update(
            {"_id": ObjectId(publication_id)},
            {
                "$inc": {
                    "likes_count": -1
                }
            }
        )
        if updated_pub is None:
            return False
        else:
            print(f'Publication \'{publication_id}\' got -1 like.')
            return True

    def downvote_one_comment(self, publication_id: str, comment_id: str) -> bool:
        updated_pub = self.collection.find_one_and_update(
            {
                "_id": ObjectId(publication_id),
                "comments._id": ObjectId(comment_id)
            },
            {
                "$inc": {
                    "comments.$.likes_count": -1
                }
            }
        )
        if updated_pub is None:
            return False
        else:
            print(f'Comment \'{comment_id}\' got -1 like.')
            return True

    def downvote_one_reply(self, publication_id: str, comment_id: str, reply_id: str) -> bool:
        updated_pub = self.collection.find_one_and_update(
            {
                "_id": ObjectId(publication_id),
                "comments._id": ObjectId(comment_id),
                "comments.replies._id": ObjectId(reply_id)
            },
            {
                "$inc": {
                    "replies.$.likes_count": -1
                }
            },
            return_document=ReturnDocument.AFTER
        )
        print(updated_pub)
        if updated_pub is None:
            return False
        else:
            print(f'Reply \'{reply_id}\' got -1 like.')
            return True

    # TODO
    def fav_publication(self) -> bool:
        pass

    def get_publications_since(self, time: datetime) -> list:
        result = self.collection.find({
            "publication_date": {'$gte': time}
        })
        pubs = []
        for doc in result:
            pubs.append(doc)
        print(str(len(pubs)) + " publications created since " + str(time) + " returned")
        return pubs

    def upload_image(self, data: bytes) -> ObjectId:
        print("New image uploaded.")
        return self.fs.put(data, content_type="image/jpeg")

    def set_url(self, publication_id: str, file_id: str) -> None:
        self.collection.find_one_and_update(
            {
                "_id": ObjectId(publication_id)
            },
            {
                "$set": {"media_url": f"/api/images/{file_id}"}
            },
        )

    def download_image(self, file_id: ObjectId) -> gridfs.GridOut:
        print(f"Image {str(file_id)} downloaded.")
        return self.fs.get(file_id)
