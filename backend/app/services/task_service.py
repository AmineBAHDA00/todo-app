from typing import List, Optional

from app.db.models.task_model import Task
from app.db import DatabaseError


class InvalidTaskIdError(ValueError):
    pass


class TaskNotFoundError(ValueError):
    pass


def get_all_tasks(user_id: Optional[str] = None) -> List[Task]:

    filter_query = {"user_id": user_id} if user_id else None
    return Task.get_all(filter_query)


def create_task(title: str, user_id: Optional[str] = None) -> Task:

    new_task = Task(id=None, title=title, completed=False, user_id=user_id)
    return new_task.save()


def delete_task(task_id: str) -> bool:

    return Task.delete(task_id)


def update_task(task_id: str, completed: bool) -> bool:

    return Task.update(task_id, {"completed": completed})
