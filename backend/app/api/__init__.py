from flask import Flask
from flask_restx import Api

from .task_resource import TaskListResource, TaskResource, ns as tasks_ns
from .user_resource import UserListResource, UserResource, UserTasksResource, ns as users_ns


def register_routes(api: Api) -> None:
    """
    Enregistre tous les namespaces de l'API.
    Cette fonction centralise l'ajout des namespaces (tasks, users, etc.).
    """
    api.add_namespace(tasks_ns, path="/tasks")
    api.add_namespace(users_ns, path="/users")


def create_api(app: Flask) -> Api:
    """
    Crée et configure l'instance d'Api Flask-RESTX,
    puis enregistre tous les namespaces.
    """
    api = Api(
        app,
        doc="/swagger/",
        title="Todo API",
        description="API pour la gestion des tâches et utilisateurs",
    )
    register_routes(api)
    return api


__all__ = [
    "TaskListResource",
    "TaskResource",
    "register_routes",
    "create_api",
    "UserListResource",
    "UserResource",
    "UserTasksResource",
]

