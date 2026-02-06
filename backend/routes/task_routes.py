from flask import Blueprint, jsonify, request
from models.task_model import (
    get_all_tasks, create_task,
    update_task, delete_task
)
from services.task_service import format_task

task_bp = Blueprint("task_routes", __name__)

@task_bp.route("/tasks", methods=["GET", "POST"])
def tasks():
    if request.method == "GET":
        tasks = [format_task(t) for t in get_all_tasks()]
        return jsonify(tasks)

    if request.method == "POST":
        data = request.json
        if not data or "title" not in data:
            return jsonify({"error": "Titre manquant"}), 400

        create_task(data["title"])
        return jsonify({"message": "Tâche ajoutée"}), 201


@task_bp.route("/tasks/<id>", methods=["PUT", "DELETE"])
def one_task(id):

    if request.method == "DELETE":
        delete_task(id)
        return jsonify({"status": "deleted"})

    if request.method == "PUT":
        data = request.json
        update_task(id, data.get("completed"))
        return jsonify({"status": "updated"})
