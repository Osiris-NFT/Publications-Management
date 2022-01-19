from fastapi import FastAPI
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

class commentModel(BaseModel):  #_id, timestamps, hashtags and likes count have to be built by the service afterward
    user: str
    content: str

class replyModel(BaseModel):
    user: str
    target_user: str
    content: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


samples = [
    {
        "_id": ObjectId(),
        "plublication_date": str(datetime.now()),
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
        "plublication_date": str(datetime.now()),
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
        "plublication_date": str(datetime.now()),
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

@app.post("/post_publication")
async def post_publication(publication: publicationModel):
    pass

@app.get("/insert_samples") # DEBUG
async def insert():
    for publication in samples:
        mongodb_interface.insert_one_publication(publication)
    return {"message": "publications posted"}


@app.get("/get/{publication_id}")
async def get_publication(publication_id: str):
    publication = mongodb_interface.get_one_publication(publication_id)
    publication['_id'] = str(publication['_id'])
    for x in range(len(publication["comments"])):
        publication['comments'][x]['_id'] = str(publication['comments'][x]['_id'])
        for y in range(len(publication['comments'][x]['replies'])):
            publication['comments'][x]['replies'][y]['_id'] = str(publication['comments'][x]['replies'][y]['_id'])
    return {
        "publication": publication
    }


@app.delete("/delete/{publication_id}")
async def delete_publication(publication_id):
    removed_publication = mongodb_interface.delete_one_publication(publication_id)
    if removed_publication != None:
        return {
            "message": f"publication {publication_id} deleted",
            "removed publication": removed_publication
        }
    else:
        response = {
            "message": f"publication {publication_id} deleted",
            "removed publication": removed_publication
        }
        response.status_code = 201
        return response
        