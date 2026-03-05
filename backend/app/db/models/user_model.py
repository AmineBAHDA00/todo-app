from dataclasses import dataclass
from typing import Any, Dict, Optional, Type, TypeVar

from app.db import Document, DatabaseError


TUser = TypeVar("TUser", bound="User")


@dataclass
class User(Document):

    collection_name: str = "users"
    invalid_id_error_class: Type[Exception] = ValueError
    not_found_error_class: Type[Exception] = DatabaseError

    id: Optional[str] = None
    name: str = ""
    email: str = ""

    @classmethod
    def from_mongo(cls: Type[TUser], doc: Dict[str, Any]) -> TUser:

        return cls(
            id=str(doc["_id"]),
            name=doc["name"],
            email=doc["email"],
        )

    def to_mongo(self) -> Dict[str, Any]:

        return {
            "name": self.name,
            "email": self.email,
        }

    def to_api(self) -> Dict[str, Any]:

        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
        }
