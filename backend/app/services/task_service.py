from typing import List, Optional

from bson import ObjectId
from bson.errors import InvalidId
import importlib

from app.models.task_model import Task, from_mongo, to_mongo


def _get_tasks_collection():

    mongo_module = importlib.import_module("app.mongoDB.db")
    if mongo_module.db is None:
        raise RuntimeError("La base de données n'est pas initialisée.")
    return mongo_module.db.tasks


def get_all_tasks() -> List[Task]:

    tasks_collection = _get_tasks_collection()
    docs = tasks_collection.find()
    return [from_mongo(doc) for doc in docs]


def create_task(title: str) -> Optional[Task]:

    tasks_collection = _get_tasks_collection()
    new_task = Task(id=None, title=title, completed=False)
    to_insert = to_mongo(new_task)
    insert_result = tasks_collection.insert_one(to_insert)

    created_doc = tasks_collection.find_one({"_id": insert_result.inserted_id})
    if not created_doc:
        return None

    return from_mongo(created_doc)


def delete_task(task_id: str) -> bool:

    try:
        object_id = ObjectId(task_id)
    except (InvalidId, TypeError):
        # id invalide -> considéré comme non trouvé
        return False

    try:
        tasks_collection = _get_tasks_collection()
        # check if exists
        existing = tasks_collection.find_one({"_id": object_id})
        if not existing:
            return False

        result = tasks_collection.delete_one({"_id": object_id})
        return result.deleted_count > 0
    except Exception:
        # en cas d'erreur DB, on ne fait pas planter l'API
        return False


def update_task(task_id: str, completed: bool) -> bool:
 
    try:
        object_id = ObjectId(task_id)
    except (InvalidId, TypeError):
        # id invalide -> considéré comme non trouvé
        return False

    try:
        tasks_collection = _get_tasks_collection()
        # check if exists
        existing = tasks_collection.find_one({"_id": object_id})
        if not existing:
            return False

        result = tasks_collection.update_one(
            {"_id": object_id},
            {"$set": {"completed": completed}},
        )
        return result.modified_count > 0
    except Exception:
        # en cas d'erreur DB, on ne fait pas planter l'API
        return False

