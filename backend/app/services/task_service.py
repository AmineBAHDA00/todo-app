from typing import List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import (
    PyMongoError,
    OperationFailure,
    ServerSelectionTimeoutError,
    ConnectionFailure,
    WriteError,
    DuplicateKeyError,
)
import importlib

from app.models.task_model import Task, from_mongo, to_mongo


# Exceptions personnalisées pour une meilleure gestion des erreurs
class InvalidTaskIdError(ValueError):
    
    pass


class TaskNotFoundError(ValueError):
    
    pass


class DatabaseError(Exception):
    
    pass


def _get_tasks_collection():

    try:
        mongo_module = importlib.import_module("app.mongoDB.db")
        if mongo_module.db is None:
            raise DatabaseError("La base de données n'est pas initialisée.")
        return mongo_module.db.tasks
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
    except Exception as e:
        raise DatabaseError(f"Erreur lors de l'accès à la collection MongoDB: {str(e)}")


def get_all_tasks(user_id: Optional[str] = None) -> List[Task]:

    try:
        tasks_collection = _get_tasks_collection()
        # Utilisation de PyMongo pour récupérer tous les documents
        if user_id:
            # Filtrer par user_id (stocké comme string dans MongoDB)
            docs = tasks_collection.find({"user_id": user_id})
        else:
            docs = tasks_collection.find()
        return [from_mongo(doc) for doc in docs]
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
    except OperationFailure as e:
        raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
    except DatabaseError:
        # Re-lancer les DatabaseError
        raise
    except PyMongoError as e:
        raise DatabaseError(f"Erreur PyMongo lors de la récupération des tâches: {str(e)}")
    except Exception as e:
        raise DatabaseError(f"Erreur inattendue lors de la récupération des tâches: {str(e)}")


def create_task(title: str, user_id: Optional[str] = None) -> Task:

    try:
        tasks_collection = _get_tasks_collection()
        new_task = Task(id=None, title=title, completed=False, user_id=user_id)
        to_insert = to_mongo(new_task)
        
        # Utilisation de insert_one() de PyMongo
        insert_result = tasks_collection.insert_one(to_insert)
        
        # Vérification que l'insertion a réussi
        if not insert_result.inserted_id:
            raise DatabaseError("Erreur: l'insertion de la tâche a échoué")
        
        # Récupération du document créé avec find_one() de PyMongo
        created_doc = tasks_collection.find_one({"_id": insert_result.inserted_id})
        if not created_doc:
            raise DatabaseError("Erreur: la tâche créée n'a pas pu être récupérée depuis la base de données")

        return from_mongo(created_doc)
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
    except WriteError as e:
        raise DatabaseError(f"Erreur d'écriture MongoDB: {str(e)}")
    except DuplicateKeyError as e:
        raise DatabaseError(f"Erreur: clé dupliquée lors de la création de la tâche: {str(e)}")
    except OperationFailure as e:
        raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
    except DatabaseError:
        # Re-lancer les DatabaseError
        raise
    except PyMongoError as e:
        raise DatabaseError(f"Erreur PyMongo lors de la création de la tâche: {str(e)}")
    except Exception as e:
        raise DatabaseError(f"Erreur inattendue lors de la création de la tâche: {str(e)}")


def delete_task(task_id: str) -> bool:

    try:
        object_id = ObjectId(task_id)
    except (InvalidId, TypeError):
        raise InvalidTaskIdError(f"ID de tâche invalide: '{task_id}'")

    try:
        tasks_collection = _get_tasks_collection()
        # Vérification de l'existence de la tâche avec find_one() de PyMongo
        existing = tasks_collection.find_one({"_id": object_id})
        if not existing:
            raise TaskNotFoundError(f"Tâche avec l'ID '{task_id}' non trouvée")

        # Utilisation de delete_one() de PyMongo
        result = tasks_collection.delete_one({"_id": object_id})
        if result.deleted_count == 0:
            raise DatabaseError(f"Erreur lors de la suppression de la tâche '{task_id}'")
        
        return True
    except (InvalidTaskIdError, TaskNotFoundError):
        # Re-lancer les exceptions spécifiques
        raise
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
    except OperationFailure as e:
        raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
    except PyMongoError as e:
        raise DatabaseError(f"Erreur PyMongo lors de la suppression de la tâche: {str(e)}")
    except Exception as e:
        raise DatabaseError(f"Erreur inattendue lors de la suppression de la tâche: {str(e)}")


def update_task(task_id: str, completed: bool) -> bool:
    try:
        object_id = ObjectId(task_id)
    except (InvalidId, TypeError):
        raise InvalidTaskIdError(f"ID de tâche invalide: '{task_id}'")

    try:
        tasks_collection = _get_tasks_collection()
        # Vérification de l'existence de la tâche avec find_one() de PyMongo
        existing = tasks_collection.find_one({"_id": object_id})
        if not existing:
            raise TaskNotFoundError(f"Tâche avec l'ID '{task_id}' non trouvée")

        # Utilisation de update_one() de PyMongo avec l'opérateur $set
        result = tasks_collection.update_one(
            {"_id": object_id},
            {"$set": {"completed": completed}},
        )
        
        if result.modified_count == 0:
            raise DatabaseError(f"Erreur lors de la mise à jour de la tâche '{task_id}'")
        
        return True
    except (InvalidTaskIdError, TaskNotFoundError):
        # Re-lancer les exceptions spécifiques
        raise
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
    except WriteError as e:
        raise DatabaseError(f"Erreur d'écriture MongoDB: {str(e)}")
    except OperationFailure as e:
        raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
    except PyMongoError as e:
        raise DatabaseError(f"Erreur PyMongo lors de la mise à jour de la tâche: {str(e)}")
    except Exception as e:
        raise DatabaseError(f"Erreur inattendue lors de la mise à jour de la tâche: {str(e)}")

