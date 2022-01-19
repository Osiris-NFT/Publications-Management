from fastapi import FastAPI
from classes.db_interface import db_interface
from bson import ObjectId
from datetime import datetime
app = FastAPI()

mongodb_interface = db_interface()
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
                    }, {}, {}
                ]
            },
            {
                "_id": ObjectId(),
                "user": "LostOnTweeter",
                "plublication_date": str(datetime.now()),
                "content": "ratio.",
                "likes_count": 327
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
    }
]
@app.get("/insert_samples")
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