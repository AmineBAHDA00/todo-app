from typing import List

from app.db.models.user_model import User
from app.db import DatabaseError


class InvalidUserIdError(ValueError):
    pass


class UserNotFoundError(ValueError):
    pass


def get_all_users() -> List[User]:

    return User.get_all()


def create_user(name: str, email: str) -> User:

    new_user = User(id=None, name=name, email=email)
    return new_user.save()


def delete_user(user_id: str) -> bool:

    return User.delete(user_id)


def update_user(user_id: str, name: str = None, email: str = None) -> bool:

    update_data = {}
    if name is not None:
        update_data["name"] = name
    if email is not None:
        update_data["email"] = email
    
    if not update_data:
        raise ValueError("Au moins un champ (name ou email) doit être fourni pour la mise à jour")
    
    return User.update(user_id, update_data)
