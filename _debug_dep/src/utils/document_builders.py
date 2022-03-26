from datetime import datetime
from bson import ObjectId

def buildComment(comment: dict) -> dict:
    hashtags = getHashtags(comment['content'])
    comment["hashtags"] = hashtags
    comment["publication_date"] = str(datetime.now())
    comment["_id"] = ObjectId()
    comment["likes_count"] = 0
    comment["replies"] = []
    return comment


def buildReply(reply: dict) -> dict:
    hashtags = getHashtags(reply['content'])
    reply["hashtags"] = hashtags
    reply["publication_date"] = str(datetime.now())
    reply["_id"] = ObjectId()
    reply["likes_count"] = 0
    return reply

def buildPublication(publication: dict) -> dict:
    hashtags = getHashtags(publication["description"])
    publication["hashtags"] = hashtags
    publication["publication_date"] = str(datetime.now())
    publication["_id"] = ObjectId()
    publication["likes_count"] = 0
    publication["comments"] = []
    return publication


def stringifyIDs(publication: dict) -> dict:
    """Stringify every ObjectId() of a mongoDB's publication"""
    publication['_id'] = str(publication['_id'])
    for x in range(len(publication["comments"])):
        publication['comments'][x]['_id'] = str(
            publication['comments'][x]['_id'])
        for y in range(len(publication['comments'][x]['replies'])):
            publication['comments'][x]['replies'][y]['_id'] = str(
                publication['comments'][x]['replies'][y]['_id'])
    return publication


def getHashtags(string: str) -> list:
    str_list = string.split(' ')
    hashtags = [wrd.strip('#')
                for wrd in str_list if wrd.lower().startswith('#')]
    return hashtags
