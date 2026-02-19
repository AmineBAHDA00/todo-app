from typing import List

from app.models.user_model import User, from_mongo, to_mongo
from app.Core import Document, DatabaseError


# Exceptions personnalisées pour une meilleure gestion des erreurs
class InvalidUserIdError(ValueError):
    
    pass


class UserNotFoundError(ValueError):
    
    pass


# Instance Document pour les utilisateurs
_user_document = Document(
    collection_name="users",
    from_mongo_func=from_mongo,
    to_mongo_func=to_mongo,
    model_class=User,
    invalid_id_error_class=InvalidUserIdError,
    not_found_error_class=UserNotFoundError
)


def get_all_users() -> List[User]:

    return _user_document.get_all()


def create_user(name: str, email: str) -> User:

    new_user = User(id=None, name=name, email=email)
    return _user_document.save(new_user)


def delete_user(user_id: str) -> bool:

    return _user_document.delete(user_id)


def update_user(user_id: str, name: str = None, email: str = None) -> bool:

    # Construction de l'objet de mise à jour
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if email is not None:
        update_data["email"] = email
    
    if not update_data:
        raise ValueError("Au moins un champ (name ou email) doit être fourni pour la mise à jour")
    
    return _user_document.update(user_id, update_data)
