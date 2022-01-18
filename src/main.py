from fastapi import FastAPI
from classes.db_interface import db_interface
app = FastAPI()

mongo = db_interface()
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/insert")
async def insert():
    mongo.insert_publication(
        {
            "test": 1
        }
    )
    return {"message": "publication posted"}
