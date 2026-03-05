from dataclasses import dataclass
from typing import Any, Dict, Optional, Type, TypeVar

from app.db import Document, DatabaseError


TTask = TypeVar("TTask", bound="Task")


@dataclass
class Task(Document):


    collection_name: str = "tasks"
    invalid_id_error_class: Type[Exception] = ValueError
    not_found_error_class: Type[Exception] = DatabaseError

    id: Optional[str] = None
    title: str = ""
    completed: bool = False
    user_id: Optional[str] = None

    @classmethod
    def from_mongo(cls: Type[TTask], doc: Dict[str, Any]) -> TTask:
        return cls(
            id=str(doc["_id"]),
            title=doc["title"],
            completed=doc.get("completed", False),
            user_id=str(doc["user_id"]) if doc.get("user_id") else None,
        )

    def to_mongo(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "title": self.title,
            "completed": self.completed,
        }
        if self.user_id is not None:
            data["user_id"] = self.user_id
        return data

    def to_api(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "user_id": self.user_id,
        }
