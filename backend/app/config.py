import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:12341234@mongodb:27017/todo_db?authSource=admin")
DB_NAME = os.getenv("DB_NAME", "todo_db")