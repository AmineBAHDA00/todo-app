from flask import request
from flask_restful import Resource, Api, fields, marshal_with, abort

from app.services import get_all_tasks, create_task, update_task, delete_task


task_fields = {
    "id": fields.String,
    "title": fields.String,
    "completed": fields.Boolean,
}

status_fields = {
    "status": fields.String,
}


class TaskListResource(Resource):
    @marshal_with(task_fields, envelope="tasks")
    def get(self):

        return get_all_tasks()

    @marshal_with(task_fields)
    def post(self):

        data = request.get_json() or {}
        if "title" not in data:
            abort(400, message="Titre manquant")

        task = create_task(data["title"])
        if task is None:
            abort(500, message="Création impossible")

        return task, 201


class TaskResource(Resource):
    @marshal_with(status_fields)
    def delete(self, id: str):
 
        deleted = delete_task(id)
        status_code = 200 if deleted else 404
        return {"status": "deleted" if deleted else "not_found"}, status_code

    @marshal_with(status_fields)
    def put(self, id: str):
 
        data = request.get_json() or {}
        completed = bool(data.get("completed"))
        updated = update_task(id, completed)
        status_code = 200 if updated else 404
        return {"status": "updated" if updated else "not_found"}, status_code


def register_routes(api: Api) -> None:

    # Routes pour la liste des tâches
    api.add_resource(TaskListResource, "/tasks")
    
    # Routes pour une tâche spécifique
    api.add_resource(TaskResource, "/tasks/<string:id>")

