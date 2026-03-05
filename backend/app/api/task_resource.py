import logging

from flask import request
from flask_restx import Resource, Api, marshal_with, abort, fields, Namespace

from app.services import (
    get_all_tasks,
    create_task,
    update_task,
    delete_task,
    InvalidTaskIdError,
    TaskNotFoundError,
    DatabaseError,
)
from app.utils.dtos.task_dto import (
    task_fields,
    status_fields,
    paginated_tasks_fields,
    task_input_fields,
    task_update_fields,
)

# Logger du module
logger = logging.getLogger(__name__)

# Namespace pour organiser les routes
ns = Namespace('tasks', description='Opérations sur les tâches')

# Modèles pour la validation avec @api.expect (basés sur les DTO)
task_input_model = ns.model("TaskInput", task_input_fields)
task_update_model = ns.model("TaskUpdate", task_update_fields)


@ns.route('')
class TaskListResource(Resource):
    @ns.marshal_with(paginated_tasks_fields)
    @ns.doc('list_tasks', description='Récupère la liste paginée des tâches')
    def get(self):

        # Récupération des paramètres de pagination
        try:
            page = int(request.args.get("page", 1))
            # Le paramètre de taille de page est nommé "size" dans l'API
            per_page = int(request.args.get("size", 10))
        except (ValueError, TypeError):
            page = 1
            per_page = 10
        
        # Validation et limites
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 10
        if per_page > 100:  # Limite maximale
            per_page = 100
        
        # Récupération des paramètres de filtrage
        user_id = request.args.get("user_id")  # Optionnel pour filtrer par utilisateur
        
        # Récupération de toutes les tâches (filtrées par user_id si fourni)
        try:
            all_tasks = get_all_tasks(user_id=user_id)
        except DatabaseError as e:
            logger.exception("Erreur de base de données lors de la récupération des tâches")
            abort(500, message="Une erreur interne est survenue lors de la récupération des tâches.")
        except Exception as e:
            logger.exception("Erreur inattendue lors de la récupération des tâches")
            abort(500, message="Une erreur inattendue est survenue lors de la récupération des tâches.")
        
        total = len(all_tasks)
        
        # Calcul de la pagination
        pages = (total + per_page - 1) // per_page if total > 0 else 0  # Arrondi vers le haut
        start = (page - 1) * per_page
        end = start + per_page
        
        # Extraction des tâches de la page demandée
        paginated_items = all_tasks[start:end]
        
        # Construction de la réponse paginée
        return {
            "items": paginated_items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": pages,
                "has_next": page < pages,
                "has_prev": page > 1,
            }
        }

    @ns.marshal_with(task_fields, code=201)
    @ns.expect(task_input_model, validate=True)
    @ns.doc('create_task', description='Crée une nouvelle tâche')
    def post(self):
        """Crée une nouvelle tâche avec validation automatique via @api.expect"""
        data = ns.payload  # Les données sont déjà validées par @api.expect
        
        user_id = data.get("user_id")
        try:
            task = create_task(data["title"], user_id=user_id)
            return task, 201
        except DatabaseError as e:
            logger.exception("Erreur de base de données lors de la création d'une tâche")
            abort(500, message="Une erreur interne est survenue lors de la création de la tâche.")
        except Exception as e:
            logger.exception("Erreur inattendue lors de la création d'une tâche")
            abort(500, message="Une erreur inattendue est survenue lors de la création de la tâche.")


@ns.route('/<string:id>')
class TaskResource(Resource):
    @ns.marshal_with(status_fields)
    @ns.doc('delete_task', description='Supprime une tâche')
    def delete(self, id: str):
        try:
            delete_task(id)
            return {"status": "deleted"}, 200
        except InvalidTaskIdError as e:
            abort(400, message=str(e))
        except TaskNotFoundError as e:
            abort(404, message=str(e))
        except DatabaseError as e:
            logger.exception("Erreur de base de données lors de la suppression d'une tâche")
            abort(500, message="Une erreur interne est survenue lors de la suppression de la tâche.")
        except Exception as e:
            logger.exception("Erreur inattendue lors de la suppression d'une tâche")
            abort(500, message="Une erreur inattendue est survenue lors de la suppression de la tâche.")

    @ns.marshal_with(status_fields)
    @ns.expect(task_update_model, validate=True)
    @ns.doc('update_task', description='Met à jour le statut completed d\'une tâche')
    def put(self, id: str):
        """Met à jour une tâche avec validation automatique via @api.expect"""
        data = ns.payload  # Les données sont déjà validées par @api.expect
        completed = data["completed"]
        
        try:
            update_task(id, completed)
            return {"status": "updated"}, 200
        except InvalidTaskIdError as e:
            abort(400, message=str(e))
        except TaskNotFoundError as e:
            abort(404, message=str(e))
        except DatabaseError as e:
            logger.exception("Erreur de base de données lors de la mise à jour d'une tâche")
            abort(500, message="Une erreur interne est survenue lors de la mise à jour de la tâche.")
        except Exception as e:
            logger.exception("Erreur inattendue lors de la mise à jour d'une tâche")
            abort(500, message="Une erreur inattendue est survenue lors de la mise à jour de la tâche.")

