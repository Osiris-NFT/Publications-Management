from datetime import datetime
from bson import ObjectId


def build_comment(comment: dict) -> dict:
    hashtags = get_hashtags(comment['content'])
    comment["hashtags"] = hashtags
    comment["publication_date"] = datetime.now()
    comment["_id"] = ObjectId()
    comment["likes_count"] = 0
    comment["replies"] = []
    return comment


def build_reply(reply: dict) -> dict:
    hashtags = get_hashtags(reply['content'])
    reply["hashtags"] = hashtags
    reply["publication_date"] = datetime.now()
    reply["_id"] = ObjectId()
    reply["likes_count"] = 0
    return reply


def build_publication(publication: dict) -> dict:
    hashtags = get_hashtags(publication["description"])
    publication["hashtags"] = hashtags
    publication["publication_date"] = datetime.now()
    publication["_id"] = ObjectId()
    publication["media_url"] = ""
    publication["likes_count"] = 0
    publication["comments"] = []
    return publication


def stringify_ids(publication: dict) -> dict:
    """Stringify every ObjectId() of a mongoDB's publication"""
    publication['_id'] = str(publication['_id'])
    for x in range(len(publication["comments"])):
        publication['comments'][x]['_id'] = str(
            publication['comments'][x]['_id'])
        for y in range(len(publication['comments'][x]['replies'])):
            publication['comments'][x]['replies'][y]['_id'] = str(
                publication['comments'][x]['replies'][y]['_id'])
    return publication


def get_hashtags(string: str) -> list:
    str_list = string.split(' ')
    hashtags = [wrd.strip('#')
                for wrd in str_list if wrd.lower().startswith('#')]
    return hashtags
