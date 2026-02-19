from typing import List, Optional, Dict, Any, TypeVar, Type, Callable
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.collection import Collection
from pymongo.errors import (
    PyMongoError,
    OperationFailure,
    ServerSelectionTimeoutError,
    ConnectionFailure,
    WriteError,
    DuplicateKeyError,
)
import importlib

# Type générique pour les modèles
T = TypeVar('T')


class DatabaseError(Exception):
  
    pass


class Document:

    
    def __init__(
        self,
        collection_name: str,
        from_mongo_func: Callable[[Dict[str, Any]], T],
        to_mongo_func: Callable[[T], Dict[str, Any]],
        model_class: Optional[Type[T]] = None,
        invalid_id_error_class: Optional[Type[Exception]] = None,
        not_found_error_class: Optional[Type[Exception]] = None
    ):
 
        self.collection_name = collection_name
        self.from_mongo = from_mongo_func
        self.to_mongo = to_mongo_func
        self.model_class = model_class
        self.invalid_id_error_class = invalid_id_error_class or ValueError
        self.not_found_error_class = not_found_error_class or DatabaseError
    
    def _get_collection(self) -> Collection:

        try:
            mongo_module = importlib.import_module("app.Core.db")
            if mongo_module.db is None:
                raise DatabaseError("La base de données n'est pas initialisée.")
            return getattr(mongo_module.db, self.collection_name)
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Erreur lors de l'accès à la collection '{self.collection_name}': {str(e)}")
    
    def save(self, entity: T) -> T:

        try:
            collection = self._get_collection()
            doc = self.to_mongo(entity)
            
            # Si l'entité a un id, on fait un update, sinon un insert
            if hasattr(entity, 'id') and entity.id:
                object_id = ObjectId(entity.id)
                result = collection.update_one(
                    {"_id": object_id},
                    {"$set": doc},
                    upsert=True
                )
                if result.upserted_id:
                    inserted_id = result.upserted_id
                else:
                    inserted_id = object_id
            else:
                # Insertion d'un nouveau document
                result = collection.insert_one(doc)
                inserted_id = result.inserted_id
            
            # Récupération du document sauvegardé
            saved_doc = collection.find_one({"_id": inserted_id})
            if not saved_doc:
                raise DatabaseError(f"Erreur: l'entité n'a pas pu être récupérée après sauvegarde")
            
            return self.from_mongo(saved_doc)
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
        except WriteError as e:
            raise DatabaseError(f"Erreur d'écriture MongoDB: {str(e)}")
        except DuplicateKeyError as e:
            raise DatabaseError(f"Erreur: clé dupliquée lors de la sauvegarde: {str(e)}")
        except OperationFailure as e:
            raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
        except PyMongoError as e:
            raise DatabaseError(f"Erreur PyMongo lors de la sauvegarde: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Erreur inattendue lors de la sauvegarde: {str(e)}")
    
    def update(self, entity_id: str, update_data: Dict[str, Any]) -> bool:

        try:
            object_id = ObjectId(entity_id)
        except (InvalidId, TypeError):
            raise self.invalid_id_error_class(f"ID invalide: '{entity_id}'")
        
        try:
            collection = self._get_collection()
            # Vérification de l'existence de l'entité
            existing = collection.find_one({"_id": object_id})
            if not existing:
                raise self.not_found_error_class(f"Entité avec l'ID '{entity_id}' non trouvée")
            
            result = collection.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                raise DatabaseError(f"Erreur lors de la mise à jour de l'entité '{entity_id}'")
            
            return True
        except (self.invalid_id_error_class, self.not_found_error_class):
            # Re-lancer les exceptions spécifiques
            raise
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
        except WriteError as e:
            raise DatabaseError(f"Erreur d'écriture MongoDB: {str(e)}")
        except OperationFailure as e:
            raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
        except PyMongoError as e:
            raise DatabaseError(f"Erreur PyMongo lors de la mise à jour: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Erreur inattendue lors de la mise à jour: {str(e)}")
    
    def update_many(self, filter_query: Dict[str, Any], update_data: Dict[str, Any]) -> int:

        try:
            collection = self._get_collection()
            result = collection.update_many(
                filter_query,
                {"$set": update_data}
            )
            return result.modified_count
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
        except WriteError as e:
            raise DatabaseError(f"Erreur d'écriture MongoDB: {str(e)}")
        except OperationFailure as e:
            raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
        except PyMongoError as e:
            raise DatabaseError(f"Erreur PyMongo lors de la mise à jour multiple: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Erreur inattendue lors de la mise à jour multiple: {str(e)}")
    
    def save_all(self, entities: List[T]) -> List[T]:

        try:
            collection = self._get_collection()
            docs_to_insert = [self.to_mongo(entity) for entity in entities]
            
            if not docs_to_insert:
                return []
            
            result = collection.insert_many(docs_to_insert)
            
            # Récupération des documents insérés
            inserted_ids = result.inserted_ids
            saved_docs = list(collection.find({"_id": {"$in": inserted_ids}}))
            
            return [self.from_mongo(doc) for doc in saved_docs]
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
        except WriteError as e:
            raise DatabaseError(f"Erreur d'écriture MongoDB: {str(e)}")
        except DuplicateKeyError as e:
            raise DatabaseError(f"Erreur: clé dupliquée lors de la sauvegarde multiple: {str(e)}")
        except OperationFailure as e:
            raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
        except PyMongoError as e:
            raise DatabaseError(f"Erreur PyMongo lors de la sauvegarde multiple: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Erreur inattendue lors de la sauvegarde multiple: {str(e)}")
    
    def upsert_all(self, entities: List[T], filter_key: str = "id") -> List[T]:

        try:
            collection = self._get_collection()
            bulk_ops = []
            
            for entity in entities:
                doc = self.to_mongo(entity)
                entity_id = getattr(entity, filter_key, None)
                
                if entity_id:
                    # Update ou insert si existe
                    filter_doc = {"_id": ObjectId(entity_id)}
                    bulk_ops.append({
                        "updateOne": {
                            "filter": filter_doc,
                            "update": {"$set": doc},
                            "upsert": True
                        }
                    })
                else:
                    # Insert simple
                    bulk_ops.append({
                        "insertOne": {
                            "document": doc
                        }
                    })
            
            if bulk_ops:
                collection.bulk_write(bulk_ops)
            
            # Récupération des documents sauvegardés
            # Note: Pour simplifier, on récupère tous les documents de la collection
            # Dans un cas réel, on pourrait optimiser en récupérant seulement ceux qui viennent d'être modifiés
            all_docs = collection.find()
            return [self.from_mongo(doc) for doc in all_docs]
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
        except WriteError as e:
            raise DatabaseError(f"Erreur d'écriture MongoDB: {str(e)}")
        except OperationFailure as e:
            raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
        except PyMongoError as e:
            raise DatabaseError(f"Erreur PyMongo lors de l'upsert multiple: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Erreur inattendue lors de l'upsert multiple: {str(e)}")
    
    def load(self, entity_id: str) -> Optional[T]:

        try:
            object_id = ObjectId(entity_id)
        except (InvalidId, TypeError):
            raise self.invalid_id_error_class(f"ID invalide: '{entity_id}'")
        
        try:
            collection = self._get_collection()
            doc = collection.find_one({"_id": object_id})
            
            if not doc:
                return None
            
            return self.from_mongo(doc)
        except self.invalid_id_error_class:
            # Re-lancer les exceptions spécifiques
            raise
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
        except OperationFailure as e:
            raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
        except PyMongoError as e:
            raise DatabaseError(f"Erreur PyMongo lors du chargement: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Erreur inattendue lors du chargement: {str(e)}")
    
    def delete(self, entity_id: str) -> bool:

        try:
            object_id = ObjectId(entity_id)
        except (InvalidId, TypeError):
            raise self.invalid_id_error_class(f"ID invalide: '{entity_id}'")
        
        try:
            collection = self._get_collection()
            # Vérification de l'existence de l'entité
            existing = collection.find_one({"_id": object_id})
            if not existing:
                raise self.not_found_error_class(f"Entité avec l'ID '{entity_id}' non trouvée")
            
            result = collection.delete_one({"_id": object_id})
            if result.deleted_count == 0:
                raise DatabaseError(f"Erreur lors de la suppression de l'entité '{entity_id}'")
            
            return True
        except (self.invalid_id_error_class, self.not_found_error_class):
            # Re-lancer les exceptions spécifiques
            raise
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
        except OperationFailure as e:
            raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
        except PyMongoError as e:
            raise DatabaseError(f"Erreur PyMongo lors de la suppression: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Erreur inattendue lors de la suppression: {str(e)}")
    
    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

        try:
            collection = self._get_collection()
            return list(collection.aggregate(pipeline))
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
        except OperationFailure as e:
            raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
        except PyMongoError as e:
            raise DatabaseError(f"Erreur PyMongo lors de l'agrégation: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Erreur inattendue lors de l'agrégation: {str(e)}")
    
    def get_all(self, filter_query: Optional[Dict[str, Any]] = None) -> List[T]:

        try:
            collection = self._get_collection()
            if filter_query:
                docs = collection.find(filter_query)
            else:
                docs = collection.find()
            return [self.from_mongo(doc) for doc in docs]
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
        except OperationFailure as e:
            raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
        except PyMongoError as e:
            raise DatabaseError(f"Erreur PyMongo lors de la récupération: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Erreur inattendue lors de la récupération: {str(e)}")
    
    def count(self, filter_query: Optional[Dict[str, Any]] = None) -> int:

        try:
            collection = self._get_collection()
            if filter_query:
                return collection.count_documents(filter_query)
            else:
                return collection.count_documents({})
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
        except OperationFailure as e:
            raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
        except PyMongoError as e:
            raise DatabaseError(f"Erreur PyMongo lors du comptage: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Erreur inattendue lors du comptage: {str(e)}")
    
    def drop(self) -> bool:

        try:
            collection = self._get_collection()
            collection.drop()
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
        except OperationFailure as e:
            raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
        except PyMongoError as e:
            raise DatabaseError(f"Erreur PyMongo lors de la suppression de la collection: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Erreur inattendue lors de la suppression de la collection: {str(e)}")
