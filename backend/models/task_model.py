from app.db import db
from bson import ObjectId

tasks_collection = db.tasks

def get_all_tasks():
    return list(tasks_collection.find())

def create_task(title):
    return tasks_collection.insert_one({"title": title, "completed": False})

def delete_task(task_id):
    return tasks_collection.delete_one({"_id": ObjectId(task_id)})

def update_task(task_id, completed):
    return tasks_collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"completed": completed}}
    )
