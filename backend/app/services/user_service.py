from typing import List

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

from app.models.user_model import User, from_mongo, to_mongo
from app.services.task_service import DatabaseError


# Exceptions personnalisées pour une meilleure gestion des erreurs
class InvalidUserIdError(ValueError):
    pass


class UserNotFoundError(ValueError):
    pass


def _get_users_collection():

    try:
        mongo_module = importlib.import_module("app.mongoDB.db")
        if mongo_module.db is None:
            raise DatabaseError("La base de données n'est pas initialisée.")
        return mongo_module.db.users
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
    except Exception as e:
        raise DatabaseError(f"Erreur lors de l'accès à la collection MongoDB: {str(e)}")


def get_all_users() -> List[User]:

    try:
        users_collection = _get_users_collection()
        # Utilisation de PyMongo pour récupérer tous les documents
        docs = users_collection.find()
        return [from_mongo(doc) for doc in docs]
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
    except OperationFailure as e:
        raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
    except DatabaseError:
        # Re-lancer les DatabaseError
        raise
    except PyMongoError as e:
        raise DatabaseError(f"Erreur PyMongo lors de la récupération des utilisateurs: {str(e)}")
    except Exception as e:
        raise DatabaseError(f"Erreur inattendue lors de la récupération des utilisateurs: {str(e)}")


def create_user(name: str, email: str) -> User:

    try:
        users_collection = _get_users_collection()
        new_user = User(id=None, name=name, email=email)
        to_insert = to_mongo(new_user)
        
        # Utilisation de insert_one() de PyMongo
        insert_result = users_collection.insert_one(to_insert)
        
        # Vérification que l'insertion a réussi
        if not insert_result.inserted_id:
            raise DatabaseError("Erreur: l'insertion de l'utilisateur a échoué")
        
        # Récupération du document créé avec find_one() de PyMongo
        created_doc = users_collection.find_one({"_id": insert_result.inserted_id})
        if not created_doc:
            raise DatabaseError("Erreur: l'utilisateur créé n'a pas pu être récupéré depuis la base de données")

        return from_mongo(created_doc)
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
    except WriteError as e:
        raise DatabaseError(f"Erreur d'écriture MongoDB: {str(e)}")
    except DuplicateKeyError as e:
        raise DatabaseError(f"Erreur: clé dupliquée lors de la création de l'utilisateur: {str(e)}")
    except OperationFailure as e:
        raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
    except DatabaseError:
        # Re-lancer les DatabaseError
        raise
    except PyMongoError as e:
        raise DatabaseError(f"Erreur PyMongo lors de la création de l'utilisateur: {str(e)}")
    except Exception as e:
        raise DatabaseError(f"Erreur inattendue lors de la création de l'utilisateur: {str(e)}")


def delete_user(user_id: str) -> bool:

    try:
        object_id = ObjectId(user_id)
    except (InvalidId, TypeError):
        raise InvalidUserIdError(f"ID d'utilisateur invalide: '{user_id}'")

    try:
        users_collection = _get_users_collection()
        # Vérification de l'existence de l'utilisateur avec find_one() de PyMongo
        existing = users_collection.find_one({"_id": object_id})
        if not existing:
            raise UserNotFoundError(f"Utilisateur avec l'ID '{user_id}' non trouvé")

        # Utilisation de delete_one() de PyMongo
        result = users_collection.delete_one({"_id": object_id})
        if result.deleted_count == 0:
            raise DatabaseError(f"Erreur lors de la suppression de l'utilisateur '{user_id}'")
        
        return True
    except (InvalidUserIdError, UserNotFoundError):
        # Re-lancer les exceptions spécifiques
        raise
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
    except OperationFailure as e:
        raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
    except PyMongoError as e:
        raise DatabaseError(f"Erreur PyMongo lors de la suppression de l'utilisateur: {str(e)}")
    except Exception as e:
        raise DatabaseError(f"Erreur inattendue lors de la suppression de l'utilisateur: {str(e)}")


def update_user(user_id: str, name: str = None, email: str = None) -> bool:

    try:
        object_id = ObjectId(user_id)
    except (InvalidId, TypeError):
        raise InvalidUserIdError(f"ID d'utilisateur invalide: '{user_id}'")

    try:
        users_collection = _get_users_collection()
        # Vérification de l'existence de l'utilisateur avec find_one() de PyMongo
        existing = users_collection.find_one({"_id": object_id})
        if not existing:
            raise UserNotFoundError(f"Utilisateur avec l'ID '{user_id}' non trouvé")

        # Construction de l'objet de mise à jour
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if email is not None:
            update_data["email"] = email
        
        if not update_data:
            raise ValueError("Au moins un champ (name ou email) doit être fourni pour la mise à jour")

        # Utilisation de update_one() de PyMongo avec l'opérateur $set
        result = users_collection.update_one(
            {"_id": object_id},
            {"$set": update_data},
        )
        
        if result.modified_count == 0:
            raise DatabaseError(f"Erreur lors de la mise à jour de l'utilisateur '{user_id}'")
        
        return True
    except (InvalidUserIdError, UserNotFoundError, ValueError):
        # Re-lancer les exceptions spécifiques
        raise
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
    except WriteError as e:
        raise DatabaseError(f"Erreur d'écriture MongoDB: {str(e)}")
    except OperationFailure as e:
        raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
    except PyMongoError as e:
        raise DatabaseError(f"Erreur PyMongo lors de la mise à jour de l'utilisateur: {str(e)}")
    except Exception as e:
        raise DatabaseError(f"Erreur inattendue lors de la mise à jour de l'utilisateur: {str(e)}")
