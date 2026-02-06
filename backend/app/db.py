from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from .config import MONGO_URI, DB_NAME

client = None
db = None

def init_db():
    global client, db

    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        print("MongoDB Connected ✔️")
    except ConnectionFailure:
        print("MongoDB Connection Error ❌")

    db = client[DB_NAME]
