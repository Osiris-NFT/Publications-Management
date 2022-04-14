from fastapi import FastAPI, Response, status, Query
from bson import ObjectId
import datetime
from typing import Optional
import json
import random
import requests
import os

from classes.db_interface import db_interface
import utils

app = FastAPI()
mongodb_interface = db_interface()

"""
# DEBUG
TRENDTRACKER_URL = "http://0.0.0.0:8080/"
"""
TRENDTRACKER_URL = os.environ["TRENDTRACKER_URL"]
TRENDTRACKER_PORT = os.environ["TRENDTRACKER_PORT"]
TRENDTRACKER_BL_ENDPOINT = "/get_new_best_publications_ids"


@app.get("/")
async def root():
    return {"message": "Publication service is alive !"}


@app.post("/post_publication",
          status_code = status.HTTP_201_CREATED,
          responses={
              400: {"description": "Wrong format."},
              201: {
                  "description": "Publication posted.",
                  "content": {
                      "application/json": {
                          "example": utils.publication_example
                      }
                  }
              }
          })
async def post_publication(posted_publication: utils.publicationModel, response: Response):
    publication = utils.buildPublication(dict(posted_publication))
    publication_id = mongodb_interface.insert_one_publication(publication)
    publication["_id"] = publication_id
    return {
        "message": "Publication posted !",
        "publication": publication
    }


@app.post("/post_comment",
          status_code=status.HTTP_201_CREATED,
          responses={
              400: {"description": "Wrong format."},
              201: {
                  "description": "Comment posted.",
                  "content": {
                      "application/json": {
                          "example": {
                              "message": "Comment successfully posted !",
                              "comment": utils.comment_example
                          }
                      }
                  }
              }
          })
async def post_a_comment(publication_id: str, posted_comment: utils.commentModel, response: Response):
    if not ObjectId.is_valid(publication_id):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "Invalid ID"
        }
    # Build comment
    comment = utils.buildComment(dict(posted_comment))
    comment_id = mongodb_interface.insert_one_comment(publication_id, comment)
    comment["_id"] = str(comment_id)
    return {
        "message": "Comment successfully posted !",
        "comment": comment
    }

@app.post("/post_reply",
          status_code=status.HTTP_201_CREATED,
          responses={
              400: {"description": "Wrong format."},
              201: {
                  "description": "Reply posted.",
                  "content": {
                      "application/json": {
                          "example": {
                              "message": "Reply successfully posted !",
                              "comment": utils.reply_example
                          }
                      }
                  }
              }
          })
async def post_a_reply(publication_id: str, comment_id: str, posted_reply: utils.replyModel, response: Response):
    if not ObjectId.is_valid(publication_id):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "Invalid ID"
        }
    # Build reply
    reply = utils.buildReply(dict(posted_reply))
    reply_id = mongodb_interface.insert_one_reply(publication_id,comment_id, reply)
    reply["_id"] = str(reply_id)
    return {
        "message": "Comment successfully posted !",
        "comment": reply
    }

@app.get("/insert_samples") # DEBUG
async def DEBUG():
    for publication in utils.samples:
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
                         "example": utils.publication_example
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
        formated_publication = utils.stringifyIDs(publication)
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
                         "example": [utils.publication_example, utils.publication_example]
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
            formated_publications.append(utils.stringifyIDs(publication))
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
                                utils.publication_example
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
        formated_publication = utils.stringifyIDs(removed_publication)
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
@app.delete("/delete_comment_by_id/{publication_id}/{comment_id}",
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
@app.delete("/delete_reply_by_id/{publication_id}/{comment_id}/{reply_id}",
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


@app.patch("/upvote_publication/{publication_id}",
           status_code=status.HTTP_200_OK,
           responses={
               400: {"description": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."},
               404: {"description": "The publication does not exit."},
               200: {
                   "description": "Publication got upvoted successfully.",
                   "content": {
                       "application/json": {
                           "example": {"message": "Publication upvoted !"}
                       }
                   }
               }
           })
async def upvote_a_publication(publication_id: str, response: Response):
    if not ObjectId.is_valid(publication_id):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."
        }
    is_success = mongodb_interface.upvote_one_publication(publication_id)
    if is_success:
        return{
            "message": "Publication upvoted !"
        }
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return{
            "message": "Publication does not exist"
        }

@app.patch("/upvote_comment/{publication_id}/{comment_id}",
            status_code = status.HTTP_200_OK,
           responses={
               400: {"description": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."},
               404: {"description": "The  or comment does not exit."},
               200: {
                   "description": "Comment got upvoted successfully.",
                   "content": {
                       "application/json": {
                           "example": {"message": "Comment upvoted !"}
                       }
                   }
               }
           })
async def upvote_a_comment(publication_id: str, comment_id: str, response: Response):
    if not (
            ObjectId.is_valid(publication_id)
            and ObjectId.is_valid(comment_id)):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."
        }
    is_success = mongodb_interface.upvote_one_comment(publication_id, comment_id)
    if is_success:
        return{
            "message": "Comment upvoted !"
        }
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return{
            "message": "Publication or comment does not exist"
        }

@app.patch("/upvote_reply/{publication_id}/{comment_id}/{reply_id}",
           status_code=status.HTTP_200_OK,
           responses={
               400: {"description": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."},
               404: {"description": "The publication, comment or reply does not exit."},
               200: {
                   "description": "Reply got upvoted successfully.",
                   "content": {
                       "application/json": {
                           "example": {"message": "Reply upvoted !"}
                       }
                   }
               }
           })
async def upvote_a_reply(publication_id: str, comment_id: str, reply_id: str, response: Response):
    if not (ObjectId.is_valid(publication_id) and ObjectId.is_valid(comment_id) and ObjectId.is_valid(reply_id)):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."
        }
    is_success = mongodb_interface.upvote_one_reply(publication_id, comment_id, reply_id)
    if is_success:
        return{
            "message": "Reply upvoted !"
        }
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return{
            "message": "Publication, comment or reply does not exist"
        }


@app.patch("/downvote_publication/{publication_id}",
           status_code=status.HTTP_200_OK,
           responses={
               400: {"description": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."},
               404: {"description": "The publication does not exit."},
               200: {
                   "description": "Publication got downvoted successfully.",
                   "content": {
                       "application/json": {
                           "example": {"message": "Publication downvoted !"}
                       }
                   }
               }
           })
def downvote_a_publication(publication_id: str, response: Response):
    if not ObjectId.is_valid(publication_id):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."
        }
    is_success = mongodb_interface.downvote_one_publication(publication_id)
    if is_success:
        return{
            "message": "Publication downvoted !"
        }
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return{
            "message": "Publication does not exist"
        }


@app.patch("/downvote_comment/{publication_id}/{comment_id}",
           status_code=status.HTTP_200_OK,
           responses={
               400: {"description": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."},
               404: {"description": "The  or comment does not exit."},
               200: {
                   "description": "Comment got downvoted successfully.",
                   "content": {
                       "application/json": {
                           "example": {"message": "Comment downvoted !"}
                       }
                   }
               }
           })
async def downvote_a_comment(publication_id: str, comment_id: str, response: Response):
    if not (
            ObjectId.is_valid(publication_id)
            and ObjectId.is_valid(comment_id)):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."
        }
    is_success = mongodb_interface.downvote_one_comment(publication_id, comment_id)
    if is_success:
        return{
            "message": "Comment downvoted !"
        }
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return{
            "message": "Publication or comment does not exist"
        }

# FIXME
@app.patch("/downvote_reply/{publication_id}/{comment_id}/{reply_id}",
           status_code=status.HTTP_200_OK,
           responses={
               400: {"description": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."},
               404: {"description": "The publication, comment or reply does not exit."},
               200: {
                   "description": "Reply got downvoted successfully.",
                   "content": {
                       "application/json": {
                           "example": {"message": "Reply downvoted !"}
                       }
                   }
               }
           })
async def downvote_a_reply(publication_id: str, comment_id: str, reply_id: str, response: Response):
    if not (ObjectId.is_valid(publication_id) and ObjectId.is_valid(comment_id) and ObjectId.is_valid(reply_id)):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."
        }
    is_success = mongodb_interface.downvote_one_reply(
        publication_id, comment_id, reply_id)
    if is_success:
        return{
            "message": "Reply downvoted !"
        }
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return{
            "message": "Publication, comment or reply does not exist"
        }


@app.get("/get_recent_publications")  # TODO DOC
async def get_recent_publications(hours_time_delta: int, response: Response):
    if hours_time_delta > 24:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "Time delta cannot be greater than 24 hours"
        }
    since_date = datetime.datetime.now() - datetime.timedelta(hours=hours_time_delta)
    db_res = mongodb_interface.get_publications_since(since_date)
    response.status_code = status.HTTP_200_OK
    formated_pubs = []
    for pub in db_res:
        formated_pubs.append(utils.stringifyIDs(pub))
    return formated_pubs


@app.get("/trend_tracker_get_recent_publications")  # TODO DOC
async def get_recent_publications_ids_and_likes(hours_time_delta: int, response: Response):
    since_date = datetime.datetime.now() - datetime.timedelta(hours=hours_time_delta)
    db_res = mongodb_interface.get_publications_since(since_date)
    response.status_code = status.HTTP_200_OK
    result = {}
    for pub in db_res:
        result[str(pub["_id"])] = pub["likes_count"]
    return result


@app.get("/trend_tracker_get_many_publications")  # TODO DOC
async def get_many_publications_ids_and_likes(id_list_str: str, response: Response):
    id_list = id_list_str.split(',')
    print(id_list)
    response_list = {}
    for _id in id_list:
        if not (ObjectId.is_valid(_id)):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "message": "One or many ID provided are not valid ObjectId, they must be 12-byte input or a 24-character hex string."
            }
        db_res = mongodb_interface.get_one_publication(publication_id=_id)
        if db_res == None:
            continue
        else:
            response_list[_id] = db_res["likes_count"]
    response.status_code = status.HTTP_200_OK
    return response_list


@app.get("/new_best_publications")  # TODO DOC TODO TESTS
async def get_new_best_publications_list(response: Response):
    try:
        get = requests.get(TRENDTRACKER_URL + ':'+ TRENDTRACKER_PORT + TRENDTRACKER_BL_ENDPOINT)
        if get.status_code == 200:
            response.status_code = status.HTTP_200_OK
            result = []
            for _id in json.loads(get.text)["new_best_ids"]:
                pub = mongodb_interface.get_one_publication(_id)
                result.append(utils.stringifyIDs(pub))
            return {
                "best_new": result
            }

        elif get.status_code == 204:
            response.status_code = status.HTTP_204_NO_CONTENT
            return {
                "message": "No new publications available."
            }
        else:
            raise Exception()
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "message": "Error while requesting new best publications."
        }
        