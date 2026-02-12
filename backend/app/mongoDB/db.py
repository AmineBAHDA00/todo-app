from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from .config import MONGO_URI, DB_NAME
import time

client = None
db = None

def init_db():
    global client, db
    max_retries = 5
    delay_seconds = 1

    for attempt in range(1, max_retries + 1):
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
            client.admin.command("ping")
            db = client[DB_NAME]
            print(f"MongoDB Connected ✔️ (tentative {attempt})")
            return
        except ConnectionFailure as e:
            print(f"MongoDB Connection Error ❌ (tentative {attempt}/{max_retries}): {e}")
            time.sleep(delay_seconds)

    # Si on arrive ici, Mongo n'est pas joignable après plusieurs essais
    client = None
    db = None
    print("MongoDB indisponible après plusieurs tentatives, l'application démarre sans base de données.")