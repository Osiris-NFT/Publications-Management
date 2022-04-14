from pydantic import BaseModel
from fastapi import Query


# _id, timestamps, hashtags and likes count have to be built by the service afterward
class PublicationModel(BaseModel):
    publication_name: str
    user_name: str
    description: str
    content_type: str = Query(None, regex="image|video|gif|tweet|audio")
    media_url: str = Query(None, regex=r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)")
    category: str = Query(None, regex="pixel-art|digital-drawing|photography")


# _id, timestamps and likes count have to be built by the service afterward
class CommentModel(BaseModel):
    user: str
    content: str


class ReplyModel(BaseModel):
    user: str
    target_user: str
    content: str
