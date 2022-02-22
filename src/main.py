from fastapi import FastAPI, Response, status, Query
from classes.db_interface import db_interface
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
import json


app = FastAPI()
mongodb_interface = db_interface()

publication_example = {
    "_id": "5bf142459b72e12b2b1b2cd",
    "publication_date": "1999-12-31 23:59:59.999999",
    "user_name": "foo",
    "content_type": "image",
    "media_url": "https://image.com/img.png",
    "category": "photography",
    "description": "this is the description",
    "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
    "likes_count": 23,
    "comments": [
        {
            "_id": "5bf142459b72e12b2b1b2ce",
            "user": "bar",
            "plublication_date": "2000-12-31 23: 59: 59.999469",
            "content": "comment example",
            "likes_count": 10,
            "replies": [
                {
                    "_id": "5bf142459b72e12b2b1b2c3",
                    "user": "foo",
                    "plublication_date": "2001-11-30 20: 10: 42.442765",
                    "target_user": "bar",
                    "content": "reply example",
                    "likes_count": 2
                }
            ]
        }
    ]
}

comment_example = {
    "_id": "5bf142459b72e12b2b1b2cd",
    "user": "foo",
    "publication_date": "1999-12-31 23:59:59.999999",
    "content": "comment example",
    "likes_count": 0,
    "replies": []
}

class publicationModel(BaseModel): #_id, timestamps, hashtags and likes count have to be built by the service afterward
    publication_name: str
    user_name: str
    content_type: str
    media_url: str = Query(None, regex="((http|https): //)(www.)?" +
                           "[a-zA-Z0-9@:%._\\+~#?&//=]" +
                           "{2,256}\\.[a-z]" +
                           "{2,6}\\b([-a-zA-Z0-9@:%" +
                           "._\\+~#?&//=]*)")
    category: str

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


# possiblement à remplacer par json.dumps
def stringifyIDs(publication: dict) -> dict:
    """Stringify every ObjectId() of a mongoDB's publication"""
    publication['_id'] = str(publication['_id'])
    for x in range(len(publication["comments"])):
        publication['comments'][x]['_id'] = str(publication['comments'][x]['_id'])
        for y in range(len(publication['comments'][x]['replies'])):
            publication['comments'][x]['replies'][y]['_id'] = str(publication['comments'][x]['replies'][y]['_id'])
    return publication

def getHashtags(string: str) -> list:
    str_list = string.split(' ')
    hashtags = [wrd.strip('#') for wrd in str_list if wrd.lower().startswith('#')]
    return hashtags

def buildComment(comment: dict) -> dict:
    hashtags = getHashtags(comment['content'])
    comment["hashtags"] = hashtags
    comment["publication_date"] = str(datetime.now())
    comment["_id"] = ObjectId()
    comment["likes_count"] = 0
    comment["replies"] = []
    return comment

@app.post("/post_publication",
          status_code = status.HTTP_201_CREATED,
          responses={
              400: {"description": "Wrong format."},
              201: {
                  "description": "Publication posted.",
                  "content": {
                      "application/json": {
                          "example": publication_example
                      }
                  }
              }
          })
async def post_publication(publication: publicationModel):
    publication["_id"] = ObjectId()
    publication["publication_date"] = datetime.now()
    publication_id = mongodb_interface.insert_one_publication(publication)
    publication["_id"] = publication_id
    return {
        "message": "Publication posted !",
        "publication": publication
    }

@app.get("/insert_samples") # DEBUG
async def DEBUG():
    for publication in samples:
        mongodb_interface.insert_one_publication(publication)
    return {"message": "samples posted"}


@app.get("/get_publication_by_id/{publication_id}",
         status_code = status.HTTP_200_OK,
         responses={
             400:{"description": "The ID provided is not a valid ObjectId, it must be 12-byte input or a 24-character hex string."},
             404:{"description": "The publication does not exit."},
             200: {
                 "description": "Publication requested by ID.",
                 "content": {
                     "application/json": {
                         "example": publication_example
                     }
                 }
             }
         })
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



@app.get("/get_publications_of_user/{user_name}",
         status_code = status.HTTP_200_OK,
         responses={
             404: {"description": "The user does not exit."},
             200: {
                 "description": "Publications of the user returned.",
                 "content": {
                     "application/json": {
                         "example": [publication_example, publication_example]
                     }
                 }
             },
             204: {
                 "description": "User have no publications.",
                 "content": {
                     "application/json": {
                         "example": {"message": "user have no publications"}
                     }
                 }
            }
         })
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


@app.delete("/delete_publication_by_id/{publication_id}",
            status_code = status.HTTP_204_NO_CONTENT,
            responses={
                400: {"description": "The ID provided is not a valid ObjectId, it must be 12-byte input or a 24-character hex string."},
                204: {
                    "description": "The publication got removed.",
                    "content": {
                        "application/json": {
                            "example":
                                publication_example
                        }
                    }
                }
            })
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


@app.delete("/delete_publications_of_user/{user_name}",
            status_code=status.HTTP_204_NO_CONTENT,
            responses={
                404: {"description": "The user does not exit."},
                204: {
                    "description": "User's publication got removed.",
                    "content": {
                        "application/json": {
                            "example": {"message": "17 publication(s) of foo removed."}
                        }
                    }
                }
            })
async def delete_publications_of_user(user_name: str):
    result = mongodb_interface.delete_user_publications(user_name)
    return {
        "message": f"{result.deleted_count} publication(s) of {user_name} removed."
    }


#Doit recup le com
@app.delete("/delete_comment",
            status_code=status.HTTP_204_NO_CONTENT,
            responses={
                400: {"description": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."},
                404: {"description": "The publication or comment does not exit."},
                204: {
                    "description": "Comment got removed.",
                    "content": {
                        "application/json": {
                            "example": {"message": "Comment: {content}; from {user}, deleted"}
                        }
                    }
                }
            })
async def delete_comment(publication_id: str, comment_id: str, response: Response):
    if not ( 
        ObjectId.is_valid(publication_id)
        and ObjectId.is_valid(comment_id) ):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."
        }
    is_success = mongodb_interface.delete_one_comment(comment_id,publication_id)
    if is_success:
        return {
            "message": "Comment successfully removed."
        }
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "message": "Publication or comment does not exist."
        }


#Doit récup la reply / possiblement delete les replies repondants a cette meme reply
@app.delete("/delete_reply",
            status_code=status.HTTP_204_NO_CONTENT,
            responses={
                400: {"description": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."},
                404: {"description": "The publication or reply does not exit."},
                204: {
                    "description": "Reply got removed.",
                    "content": {
                        "application/json": {
                            "example": {"message": "Reply: {content}; from {user}, deleted"}
                        }
                    }
                }
            })
async def delete_reply(publication_id: str, comment_id: str, reply_id: str, response: Response):
    if not (
            ObjectId.is_valid(publication_id)
            and ObjectId.is_valid(reply_id)):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."
        }
    is_success = mongodb_interface.delete_one_reply(reply_id, comment_id, publication_id)
    if is_success:
        return {
            "message": "Reply successfully removed."
        }
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "message": "Publication, comment or reply does not exist."
        }


@app.patch("/like_publication",
           status_code=status.HTTP_200_OK,
           responses={
               400: {"description": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."},
               404: {"description": "The publication does not exit."},
               200: {
                   "description": "Publication got liked successfully.",
                   "content": {
                       "application/json": {
                           "example": {"message": "Publication liked !"}
                       }
                   }
               }
           })
async def like_a_publication(publication_id: str, response: Response):
    if not ObjectId.is_valid(publication_id):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."
        }
    is_success = mongodb_interface.like_one_publication(publication_id)
    if is_success:
        return{
            "message": "Publication liked !"
        }
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return{
            "message": "Publication does not exist"
        }

@app.patch("/like_comment", 
            status_code = status.HTTP_200_OK,
           responses={
               400: {"description": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."},
               404: {"description": "The  or comment does not exit."},
               200: {
                   "description": "Comment got liked successfully.",
                   "content": {
                       "application/json": {
                           "example": {"message": "Comment liked !"}
                       }
                   }
               }
           })
async def like_a_comment(publication_id: str, comment_id: str, response: Response):
    if not (
            ObjectId.is_valid(publication_id)
            and ObjectId.is_valid(comment_id)):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."
        }
    is_success = mongodb_interface.like_one_comment(publication_id, comment_id)
    if is_success:
        return{
            "message": "Comment liked !"
        }
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return{
            "message": "Publication or comment does not exist"
        }


@app.post("/post_comment",
            status_code = status.HTTP_201_CREATED,
            responses={
                400: {"description": "Wrong format."},
                201: {
                    "description": "Comment posted.",
                    "content": {
                        "application/json": {
                            "example": {
                                "message": "Comment successfully posted !",
                                "comment": comment_example
                            }
                        }
                    }
                }
            })
async def post_a_comment(publication_id: str, posted_comment: commentModel, response: Response):
    if not ObjectId.is_valid(publication_id):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "Invalid ID"
        }
    # Build comment
    comment = buildComment(dict(posted_comment))
    comment_id = mongodb_interface.post_one_comment(publication_id, comment)
    comment["_id"] = str(comment_id)
    return {
        "message": "Comment successfully posted !",
        "comment": comment
    }

samples = [
    {
        "_id": ObjectId(),
        "publication_date": str(datetime.now()),
        "publication_name": "Chat Qui Fly",
        "user_name": "EliseLaBalise",
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
        "publication_name": "Let Me In",
        "user_name": "EliseLaBalise",
        "content_type": "image",
        "media_url": "https://http.cat/401",
        "category": "photography",
        "description": "bruh wth my cat doin",
        "hashtags": ["#cat", "#401", "#solost"],
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
        "publication_name": "Good Meal",
        "user_name": "EliseLaBalise",
        "content_type": "image",
        "media_url": "https://http.cat/405",
        "category": "photography",
        "description": "Poor cat vs hungry man",
        "hashtags": ["#poor", "#steak"],
        "likes_count": 195,
        "comments":[
            {
                "_id": ObjectId(),
                "user": "NotMyBusiness",
                "plublication_date": str(datetime.now()),
                "content": "Noooooooooo",
                "likes_count": 10,
                "replies": [
                    {
                        "_id": ObjectId(),
                        "user": "Joykiller",
                        "plublication_date": str(datetime.now()),
                        "target_user": "NotMyBusiness",
                        "content": "RUNNN",
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
