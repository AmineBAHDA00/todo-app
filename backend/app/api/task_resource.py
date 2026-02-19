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
from app.utils.dtos.task_dto import task_fields, status_fields, paginated_tasks_fields

# Namespace pour organiser les routes
ns = Namespace('tasks', description='Opérations sur les tâches')

# Modèles pour la validation avec @api.expect
task_input_model = ns.model('TaskInput', {
    'title': fields.String(required=True, description='Titre de la tâche'),
    'user_id': fields.String(required=False, description='ID de l\'utilisateur propriétaire (optionnel)')
})

task_update_model = ns.model('TaskUpdate', {
    'completed': fields.Boolean(required=True, description='Statut de complétion de la tâche')
})


@ns.route('')
class TaskListResource(Resource):
    @ns.marshal_with(paginated_tasks_fields)
    @ns.doc('list_tasks', description='Récupère la liste paginée des tâches')
    def get(self):

        # Récupération des paramètres de pagination
        try:
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", 10))
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
            abort(500, message=str(e))
        except Exception as e:
            abort(500, message=f"Erreur lors de la récupération des tâches: {str(e)}")
        
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
        
        user_id = data.get("user_id")  # Optionnel
        try:
            task = create_task(data["title"], user_id=user_id)
            return task, 201
        except DatabaseError as e:
            abort(500, message=str(e))
        except Exception as e:
            abort(500, message=f"Erreur lors de la création de la tâche: {str(e)}")


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
            abort(500, message=str(e))

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
            abort(500, message=str(e))


def register_routes(api: Api) -> None:
    """Enregistre les routes des tâches avec validation via @api.expect"""
    api.add_namespace(ns, path='/tasks')

