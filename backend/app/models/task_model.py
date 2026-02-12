from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Task:
 

    id: Optional[str]
    title: str
    completed: bool = False

    @classmethod
    def from_mongo(cls, doc: Dict[str, Any]) -> "Task":
        
        return cls(
            id=str(doc["_id"]),
            title=doc["title"],
            completed=doc.get("completed", False),
        )

    def to_mongo(self) -> Dict[str, Any]:
        
        return {
            "title": self.title,
            "completed": self.completed,
        }

    def to_api(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
        }

