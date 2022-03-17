
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

reply_example = {
    "_id": "5bf142459b72e12b2b1b2cd",
    "user": "foo",
    "target_user": "bar",
    "publication_date": "1999-12-31 23:59:59.999999",
    "content": "reply example",
    "likes_count": 0,
}
