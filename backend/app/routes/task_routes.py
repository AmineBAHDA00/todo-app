from flask import Blueprint, request
from app.services import get_all_tasks, create_task, update_task, delete_task
from app.utils import success_response, error_response, status_response

task_bp = Blueprint("task_routes", __name__)

@task_bp.route("/tasks", methods=["GET", "POST"])
def tasks():
    if request.method == "GET":
        # La couche service renvoie des objets `Task`
        tasks = get_all_tasks()
        # On délègue le marshalling aux modèles (to_api)
        return success_response({"tasks": [t.to_api() for t in tasks]})

    if request.method == "POST":
        data = request.get_json() or {}
        if not data or "title" not in data:
            return error_response("Titre manquant", 400, code="MISSING_TITLE")

        created = create_task(data["title"])
        if created is None:
            return error_response("Création impossible", 500)
        return success_response(created.to_api(), 201)


@task_bp.route("/tasks/<id>", methods=["PUT", "DELETE"])
def one_task(id):

    if request.method == "DELETE":
        deleted = delete_task(id)
        status_code = 200 if deleted else 404
        return status_response("deleted" if deleted else "not_found", status_code)

    if request.method == "PUT":
        data = request.get_json() or {}
        completed = bool(data.get("completed"))
        updated = update_task(id, completed)
        status_code = 200 if updated else 404
        return status_response("updated" if updated else "not_found", status_code)
