from pydantic import BaseModel
from fastapi import Query


# _id, timestamps, hashtags and likes count have to be built by the service afterward
class publicationModel(BaseModel):
    publication_name: str
    user_name: str
    description: str
    content_type: str = Query(None, regex="image|video|gif|tweet|audio")
    media_url: str #= Query(None, regex="((http|https): //)(www.)?" +
                   #        "[a-zA-Z0-9@:%._\\+~#?&//=]" +
                   #        "{2,256}\\.[a-z]" +
                   #        "{2,6}\\b([-a-zA-Z0-9@:%" +
                   #        "._\\+~#?&//=]*)")
    category: str = Query(None, regex="pixel-art|digital-drawing|photography")


# _id, timestamps and likes count have to be built by the service afterward
class commentModel(BaseModel):
    user: str
    content: str


class replyModel(BaseModel):
    user: str
    target_user: str
    content: str
