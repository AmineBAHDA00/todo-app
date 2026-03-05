from typing import List, Optional, Dict, Any, TypeVar, Type
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

# Type générique pour les sous-classes de Document
T = TypeVar("T", bound="Document")


class DatabaseError(Exception):
  
    pass


class Document:

    # Ces attributs sont destinés à être surchargés dans les sous-classes
    collection_name: str = ""
    invalid_id_error_class: Type[Exception] = ValueError
    not_found_error_class: Type[Exception] = DatabaseError

    @classmethod
    def _get_collection(cls) -> Collection:

        try:
            mongo_module = importlib.import_module("app.db.db")
            if mongo_module.db is None:
                raise DatabaseError("La base de données n'est pas initialisée.")
            return getattr(mongo_module.db, cls.collection_name)
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Erreur lors de l'accès à la collection '{cls.collection_name}': {str(e)}")

    # Les sous-classes doivent implémenter ces deux méthodes
    @classmethod
    def from_mongo(cls: Type[T], doc: Dict[str, Any]) -> T:
        raise NotImplementedError

    def to_mongo(self) -> Dict[str, Any]:
        raise NotImplementedError

    def save(self: T) -> T:

        try:
            collection = self._get_collection()
            doc = self.to_mongo()
            
            # Si l'entité a un id, on fait un update, sinon un insert
            if getattr(self, "id", None):
                object_id = ObjectId(self.id)
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
                raise DatabaseError("Erreur: l'entité n'a pas pu être récupérée après sauvegarde")
            
            return self.from_mongo(saved_doc)  # type: ignore[return-value]
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
    
    @classmethod
    def update(cls, entity_id: str, update_data: Dict[str, Any]) -> bool:

        try:
            object_id = ObjectId(entity_id)
        except (InvalidId, TypeError):
            # ID invalide: on remonte l'exception spécifique configurée sur la sous-classe
            raise cls.invalid_id_error_class(f"ID invalide: '{entity_id}'")
        
        try:
            collection = cls._get_collection()
            # Utilisation d'un upsert pour créer le document s'il n'existe pas encore
            result = collection.update_one(
                {"_id": object_id},
                {"$set": update_data},
                upsert=True,
            )
            
            # Si ni mise à jour ni insertion, quelque chose s'est mal passé
            if result.matched_count == 0 and result.upserted_id is None:
                raise DatabaseError(f"Erreur lors de la mise à jour de l'entité '{entity_id}'")
            
            return True
        except cls.invalid_id_error_class:
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
    
    @classmethod
    def update_many(cls, filter_query: Dict[str, Any], update_data: Dict[str, Any]) -> int:

        try:
            collection = cls._get_collection()
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
    
    @classmethod
    def save_all(cls: Type[T], entities: List[T]) -> List[T]:

        try:
            collection = cls._get_collection()
            docs_to_insert = [entity.to_mongo() for entity in entities]
            
            if not docs_to_insert:
                return []
            
            result = collection.insert_many(docs_to_insert)
            
            # Récupération des documents insérés
            inserted_ids = result.inserted_ids
            saved_docs = list(collection.find({"_id": {"$in": inserted_ids}}))
            
            return [cls.from_mongo(doc) for doc in saved_docs]
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
    
    @classmethod
    def upsert_all(cls: Type[T], entities: List[T], filter_key: str = "id") -> List[T]:

        try:
            collection = cls._get_collection()
            bulk_ops = []
            
            for entity in entities:
                doc = entity.to_mongo()
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
                collection.bulk_write(bulk_ops)  # type: ignore[arg-type]
            
            # Récupération des documents sauvegardés
            # Note: Pour simplifier, on récupère tous les documents de la collection
            # Dans un cas réel, on pourrait optimiser en récupérant seulement ceux qui viennent d'être modifiés
            all_docs = collection.find()
            return [cls.from_mongo(doc) for doc in all_docs]
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
    
    @classmethod
    def load(cls: Type[T], entity_id: str) -> Optional[T]:

        try:
            object_id = ObjectId(entity_id)
        except (InvalidId, TypeError):
            raise cls.invalid_id_error_class(f"ID invalide: '{entity_id}'")
        
        try:
            collection = cls._get_collection()
            doc = collection.find_one({"_id": object_id})
            
            if not doc:
                return None
            
            return cls.from_mongo(doc)
        except cls.invalid_id_error_class:
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
    
    @classmethod
    def delete(cls, entity_id: str) -> bool:

        try:
            object_id = ObjectId(entity_id)
        except (InvalidId, TypeError):
            raise cls.invalid_id_error_class(f"ID invalide: '{entity_id}'")
        
        try:
            collection = cls._get_collection()
            # Vérification de l'existence de l'entité
            existing = collection.find_one({"_id": object_id})
            if not existing:
                raise cls.not_found_error_class(f"Entité avec l'ID '{entity_id}' non trouvée")
            
            result = collection.delete_one({"_id": object_id})
            if result.deleted_count == 0:
                raise DatabaseError(f"Erreur lors de la suppression de l'entité '{entity_id}'")
            
            return True
        except (cls.invalid_id_error_class, cls.not_found_error_class):
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
    
    @classmethod
    def aggregate(cls, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

        try:
            collection = cls._get_collection()
            return list(collection.aggregate(pipeline))
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
        except OperationFailure as e:
            raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
        except PyMongoError as e:
            raise DatabaseError(f"Erreur PyMongo lors de l'agrégation: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Erreur inattendue lors de l'agrégation: {str(e)}")
    
    @classmethod
    def get_all(cls: Type[T], filter_query: Optional[Dict[str, Any]] = None) -> List[T]:

        try:
            collection = cls._get_collection()
            if filter_query:
                docs = collection.find(filter_query)
            else:
                docs = collection.find()
            return [cls.from_mongo(doc) for doc in docs]
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise DatabaseError(f"Erreur de connexion MongoDB: {str(e)}")
        except OperationFailure as e:
            raise DatabaseError(f"Erreur lors de l'opération MongoDB: {str(e)}")
        except PyMongoError as e:
            raise DatabaseError(f"Erreur PyMongo lors de la récupération: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Erreur inattendue lors de la récupération: {str(e)}")
    
    @classmethod
    def count(cls, filter_query: Optional[Dict[str, Any]] = None) -> int:

        try:
            collection = cls._get_collection()
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
    
    @classmethod
    def drop(cls) -> bool:

        try:
            collection = cls._get_collection()
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
