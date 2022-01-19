from fastapi import FastAPI, Response, status
from classes.db_interface import db_interface
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


app = FastAPI()
mongodb_interface = db_interface()

class publicationModel(BaseModel): #_id, timestamps, hashtags and likes count have to be built by the service afterward
    publication_name: str
    user_name: str
    content_type: "image" or "video" or "gif" or "audio" or "tweet"
    media_url: str
    category: "photography" or "pixel-art" or "digital-drawing"

class commentModel(BaseModel):  #_id, timestamps and likes count have to be built by the service afterward
    user: str
    content: str

class replyModel(BaseModel):
    user: str
    target_user: str
    content: str


@app.get("/")
async def root():
    return {"message": "Publication service is alive !"}



def stringifyIDs(publication: dict) -> dict:
    """Stringify every ObjectId() of a mongoDB's publication"""
    publication['_id'] = str(publication['_id'])
    for x in range(len(publication["comments"])):
        publication['comments'][x]['_id'] = str(publication['comments'][x]['_id'])
        for y in range(len(publication['comments'][x]['replies'])):
            publication['comments'][x]['replies'][y]['_id'] = str(publication['comments'][x]['replies'][y]['_id'])
    return publication

"""
@app.post("/post_publication", status_code = status.HTTP_201_CREATED, response_model=publicationModel)
async def post_publication(publication: publicationModel):
    publication["_id"] = ObjectId()
    publication["publication_date"] = datetime.now()
    publication_id = mongodb_interface.insert_one_publication(publication)
    publication["_id"] = publication_id
    return {
        "message": "Publication posted !",
        "publication": publication
    }
"""
@app.get("/insert_samples") # DEBUG
async def insert_sample():
    for publication in samples:
        mongodb_interface.insert_one_publication(publication)
    return {"message": "samples posted"}


@app.get("/get_publication_by_id/{publication_id}", status_code = status.HTTP_200_OK)
async def get_publication(publication_id: str, response: Response):
    if not ObjectId.is_valid(publication_id):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "Invalid ID"
        }

    publication = mongodb_interface.get_one_publication(publication_id)
    if publication != None:
        formated_publication = stringifyIDs(publication)
        return {
            "publication": formated_publication
        }
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "message": "publication does not exist"
        }



@app.get("/get_publications_of_one_user/{user_name}", status_code = status.HTTP_200_OK)
async def get_user_publications(user_name: str, response: Response):
    publications = mongodb_interface.get_user_publications(user_name)
    if publications != []:
        formated_publications = []
        for publication in publications:
            formated_publications.append(stringifyIDs(publication))
        return {
            "message": "publications returned",
            "publications": formated_publications
        }
    else:
        response.status_code = status.HTTP_204_NO_CONTENT
        return {
            "message": "user have no publications"
        }


@app.delete("/delete/{publication_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_publication(publication_id: str ,response: Response):
    if not ObjectId.is_valid(publication_id):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "Invalid ID"
        }

    removed_publication = mongodb_interface.delete_one_publication(publication_id)
    if removed_publication != None:
        formated_publication = stringifyIDs(removed_publication)
        return {
            "message": f"publication {publication_id} deleted",
            "removed publication": formated_publication
        }
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "message": "No publication to delete"
        }
        

samples = [
    {
        "_id": ObjectId(),
        "publication_date": str(datetime.now()),
        "publication_name": "sample 1",
        "user_name": "user 1",
        "content_type": "image",
        "media_url": "https://http.cat/100",
        "category": "photography",
        "description": "this is just a cat :))",
        "hashtags": ["#cat", "#cute", "#theywillkillyou"],
        "likes_count": 23,
        "comments":[
            {
                "_id": ObjectId(),
                "user": "mamamiaDu93",
                "plublication_date": str(datetime.now()),
                "content": "to cute for me i'm dying xO",
                "likes_count": 10,
                "replies": [
                    {
                        "_id": ObjectId(),
                        "user": "notsusatall",
                        "plublication_date": str(datetime.now()),
                        "target_user": "mamamiaDu93",
                        "content": "Right bro :3",
                        "likes_count": 2
                    }
                ]
            },
            {
                "_id": ObjectId(),
                "user": "LostOnTweeter",
                "plublication_date": str(datetime.now()),
                "content": "ratio.",
                "likes_count": 327,
                "replies": []
            }
        ]
    },
    {
        "_id": ObjectId(),
        "publication_date": str(datetime.now()),
        "publication_name": "sample 2",
        "user_name": "Ayaya",
        "content_type": "image",
        "media_url": "https://http.cat/404",
        "category": "photography",
        "description": "bruh wth my cat doin",
        "hashtags": ["#cat", "#404", "#solost"],
        "likes_count": 203,
        "comments":[
            {
                "_id": ObjectId(),
                "user": "jokesterdu13",
                "plublication_date": str(datetime.now()),
                "content": "where the cat lol",
                "likes_count": 10,
                "replies": [
                    {
                        "_id": ObjectId(),
                        "user": "Ayaya",
                        "plublication_date": str(datetime.now()),
                        "target_user": "jokesterdu13",
                        "content": "ahah",
                        "likes_count": 5
                    },
                    {
                        "_id": ObjectId(),
                        "user": "ImBored",
                        "plublication_date": str(datetime.now()),
                        "target_user": "Ayaya",
                        "content": "Not impressed, maybe you meant 'haha' ?",
                        "likes_count": 0
                    }
                ]
            }
        ]
    },
    {
        "_id": ObjectId(),
        "publication_date": str(datetime.now()),
        "publication_name": "sample 3",
        "user_name": "Mamamia",
        "content_type": "image",
        "media_url": "https://http.cat/201",
        "category": "photography",
        "description": "buy this plz im poor",
        "hashtags": ["#poor", "#trump2024"],
        "likes_count": 1,
        "comments":[
            {
                "_id": ObjectId(),
                "user": "NotMyBusiness",
                "plublication_date": str(datetime.now()),
                "content": "No Thank you",
                "likes_count": 10,
                "replies": [
                    {
                        "_id": ObjectId(),
                        "user": "Joykiller",
                        "plublication_date": str(datetime.now()),
                        "target_user": "NotMyBusiness",
                        "content": "yeyeyeye, fml",
                        "likes_count": 4
                    }
                ]
            },
            {
                "_id": ObjectId(),
                "user": "MaevaDu93",
                "plublication_date": str(datetime.now()),
                "content": "Le J c'est le S.",
                "likes_count": 27,
                "replies": [
                    {
                        "_id": ObjectId(),
                        "user": "ChocolatineMaster",
                        "plublication_date": str(datetime.now()),
                        "target_user": "MaevaDu93",
                        "content": "jajaja",
                        "likes_count": 5
                    },
                    {
                        "_id": ObjectId(),
                        "user": "Ayaya",
                        "plublication_date": str(datetime.now()),
                        "target_user": "MaevaDu93",
                        "content": "C marseille bb",
                        "likes_count": 1
                    }
                ]
            }
        ]
    }
]
