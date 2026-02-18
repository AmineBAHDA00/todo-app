from dataclasses import dataclass
from typing import Any, Dict, Optional

from marshmallow import Schema, fields, post_load


@dataclass
class Task:


    id: Optional[str]
    title: str
    completed: bool = False
    user_id: Optional[str] = None


class TaskSchema(Schema):


    id = fields.Str(allow_none=True, dump_only=True)
    title = fields.Str(required=True)
    completed = fields.Bool(missing=False)
    user_id = fields.Str(allow_none=True, required=False)

    @post_load
    def make_task(self, data, **kwargs):
        
        return Task(id=None, **data)

    class Meta:
        
        ordered = True


# Instance unique du schéma (réutilisable)
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)


def from_mongo(doc: Dict[str, Any]) -> Task:

    return Task(
        id=str(doc["_id"]),
        title=doc["title"],
        completed=doc.get("completed", False),
        user_id=str(doc["user_id"]) if doc.get("user_id") else None,
    )


def to_mongo(task: Task) -> Dict[str, Any]:

    data = task_schema.dump(task)
    # On retire l'id car MongoDB le gère
    data.pop("id", None)
    # Si user_id est None, on ne l'inclut pas dans le document MongoDB
    if data.get("user_id") is None:
        data.pop("user_id", None)
    return data


def to_api(task: Task) -> Dict[str, Any]:

    return task_schema.dump(task)

