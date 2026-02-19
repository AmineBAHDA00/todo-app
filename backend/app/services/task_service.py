from typing import List, Optional

from app.models.task_model import Task, from_mongo, to_mongo
from app.Core import Document, DatabaseError


# Exceptions personnalisées pour une meilleure gestion des erreurs
class InvalidTaskIdError(ValueError):
    
    pass


class TaskNotFoundError(ValueError):
    
    pass


# Instance Document pour les tâches
_task_document = Document(
    collection_name="tasks",
    from_mongo_func=from_mongo,
    to_mongo_func=to_mongo,
    model_class=Task,
    invalid_id_error_class=InvalidTaskIdError,
    not_found_error_class=TaskNotFoundError
)


def get_all_tasks(user_id: Optional[str] = None) -> List[Task]:

    filter_query = {"user_id": user_id} if user_id else None
    return _task_document.get_all(filter_query)


def create_task(title: str, user_id: Optional[str] = None) -> Task:
  
    new_task = Task(id=None, title=title, completed=False, user_id=user_id)
    return _task_document.save(new_task)


def delete_task(task_id: str) -> bool:

    return _task_document.delete(task_id)


def update_task(task_id: str, completed: bool) -> bool:

    return _task_document.update(task_id, {"completed": completed})
