from typing import List, Optional

from bson import ObjectId
from bson.errors import InvalidId
import importlib

from app.models.task_model import Task


def _get_tasks_collection():
    """
    Récupère la collection MongoDB pour les tâches.
    Lève une erreur si la base n'est pas initialisée.
    """
    mongo_module = importlib.import_module("app.mongoDB.db")
    if mongo_module.db is None:
        raise RuntimeError("La base de données n'est pas initialisée.")
    return mongo_module.db.tasks


def get_all_tasks() -> List[Task]:
    """
    Récupère toutes les tâches sous forme d'objets domaine `Task`.
    """
    tasks_collection = _get_tasks_collection()
    docs = tasks_collection.find()
    return [Task.from_mongo(doc) for doc in docs]


def create_task(title: str) -> Optional[Task]:
    """
    Crée une nouvelle tâche et renvoie l'objet `Task` créé.
    """
    tasks_collection = _get_tasks_collection()
    to_insert = Task(id=None, title=title, completed=False).to_mongo()
    insert_result = tasks_collection.insert_one(to_insert)

    created_doc = tasks_collection.find_one({"_id": insert_result.inserted_id})
    if not created_doc:
        return None

    return Task.from_mongo(created_doc)


def delete_task(task_id: str) -> bool:
    """
    Supprime une tâche. Retourne True si une tâche a été supprimée.
    """
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
    """
    Met à jour le statut `completed` d'une tâche.
    """
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

