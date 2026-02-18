from dataclasses import dataclass
from typing import Any, Dict, Optional

from marshmallow import Schema, fields, post_load


@dataclass
class User:

    id: Optional[str]
    name: str
    email: str


class UserSchema(Schema):

    id = fields.Str(allow_none=True, dump_only=True)
    name = fields.Str(required=True)
    email = fields.Str(required=True)

    @post_load
    def make_user(self, data, **kwargs):
        
        return User(id=None, **data)

    class Meta:
        
        ordered = True


# Instance unique du schéma (réutilisable)
user_schema = UserSchema()
users_schema = UserSchema(many=True)


def from_mongo(doc: Dict[str, Any]) -> User:

    return User(
        id=str(doc["_id"]),
        name=doc["name"],
        email=doc["email"],
    )


def to_mongo(user: User) -> Dict[str, Any]:

    data = user_schema.dump(user)
    # On retire l'id car MongoDB le gère
    data.pop("id", None)
    return data


def to_api(user: User) -> Dict[str, Any]:

    return user_schema.dump(user)
