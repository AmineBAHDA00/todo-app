from dataclasses import dataclass
from typing import Any, Dict, Optional

from marshmallow import Schema, fields, post_load


@dataclass
class Task:


    id: Optional[str]
    title: str
    completed: bool = False


class TaskSchema(Schema):


    id = fields.Str(allow_none=True, dump_only=True)
    title = fields.Str(required=True)
    completed = fields.Bool(missing=False)

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
    )


def to_mongo(task: Task) -> Dict[str, Any]:

    data = task_schema.dump(task)
    # On retire l'id car MongoDB le gère
    data.pop("id", None)
    return data


def to_api(task: Task) -> Dict[str, Any]:

    return task_schema.dump(task)

