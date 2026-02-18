from flask import request
from flask_restx import Resource, Api, marshal_with, abort, fields, Namespace

from app.services import (
    get_all_users,
    create_user,
    update_user,
    delete_user,
    get_all_tasks,
    InvalidUserIdError,
    UserNotFoundError,
    DatabaseError,
)
from app.utils.dtos.user_dto import user_fields, user_with_tasks_fields, paginated_users_fields
from app.utils.dtos.task_dto import status_fields, paginated_tasks_fields
from app.models.user_model import to_api as user_to_api
from app.models.task_model import to_api as task_to_api

# Namespace pour organiser les routes
ns = Namespace('users', description='Opérations sur les utilisateurs')

# Modèles pour la validation avec @api.expect
user_input_model = ns.model('UserInput', {
    'name': fields.String(required=True, description='Nom de l\'utilisateur'),
    'email': fields.String(required=True, description='Email de l\'utilisateur')
})

user_update_model = ns.model('UserUpdate', {
    'name': fields.String(required=False, description='Nom de l\'utilisateur (optionnel)'),
    'email': fields.String(required=False, description='Email de l\'utilisateur (optionnel)')
})


@ns.route('')
class UserListResource(Resource):
    @ns.marshal_with(paginated_users_fields)
    @ns.doc('list_users', description='Récupère la liste paginée des utilisateurs avec leurs tâches')
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
        
        # Récupération de tous les utilisateurs
        try:
            all_users = get_all_users()
        except DatabaseError as e:
            abort(500, message=str(e))
        except Exception as e:
            abort(500, message=f"Erreur lors de la récupération des utilisateurs: {str(e)}")
        
        total = len(all_users)
        
        # Calcul de la pagination
        pages = (total + per_page - 1) // per_page if total > 0 else 0  # Arrondi vers le haut
        start = (page - 1) * per_page
        end = start + per_page
        
        # Extraction des utilisateurs de la page demandée
        paginated_users = all_users[start:end]
        
        # Enrichissement de chaque utilisateur avec ses tâches
        users_with_tasks = []
        try:
            for user in paginated_users:
                user_dict = user_to_api(user)
                # Récupération des tâches de l'utilisateur
                user_tasks = get_all_tasks(user_id=str(user.id))
                user_dict["tasks"] = [task_to_api(task) for task in user_tasks]
                users_with_tasks.append(user_dict)
        except DatabaseError as e:
            abort(500, message=str(e))
        except Exception as e:
            abort(500, message=f"Erreur lors de la récupération des tâches: {str(e)}")
        
        # Construction de la réponse paginée
        return {
            "items": users_with_tasks,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": pages,
                "has_next": page < pages,
                "has_prev": page > 1,
            }
        }

    @ns.marshal_with(user_fields, code=201)
    @ns.expect(user_input_model, validate=True)
    @ns.doc('create_user', description='Crée un nouvel utilisateur')
    def post(self):
        """Crée un nouvel utilisateur avec validation automatique via @api.expect"""
        data = ns.payload  # Les données sont déjà validées par @api.expect
        name = data["name"]
        email = data["email"]

        try:
            user = create_user(name, email)
            return user, 201
        except DatabaseError as e:
            abort(500, message=str(e))
        except Exception as e:
            abort(500, message=f"Erreur lors de la création de l'utilisateur: {str(e)}")


@ns.route('/<string:id>')
class UserResource(Resource):
    @ns.marshal_with(user_with_tasks_fields)
    @ns.doc('get_user', description='Récupère un utilisateur spécifique avec ses tâches')
    def get(self, id: str):

        try:
            # Récupération de tous les utilisateurs pour trouver celui demandé
            users = get_all_users()
            user = None
            for u in users:
                if str(u.id) == id:
                    user = u
                    break
            
            if not user:
                abort(404, message=f"Utilisateur avec l'ID '{id}' non trouvé")
            
            # Conversion en dictionnaire
            user_dict = user_to_api(user)
            
            # Récupération des tâches de l'utilisateur
            user_tasks = get_all_tasks(user_id=str(user.id))
            user_dict["tasks"] = [task_to_api(task) for task in user_tasks]
            
            return user_dict
        except InvalidUserIdError as e:
            abort(400, message=str(e))
        except UserNotFoundError as e:
            abort(404, message=str(e))
        except DatabaseError as e:
            abort(500, message=str(e))
        except Exception as e:
            abort(500, message=f"Erreur lors de la récupération de l'utilisateur: {str(e)}")

    @ns.marshal_with(status_fields)
    @ns.doc('delete_user', description='Supprime un utilisateur')
    def delete(self, id: str):
        try:
            delete_user(id)
            return {"status": "deleted"}, 200
        except InvalidUserIdError as e:
            abort(400, message=str(e))
        except UserNotFoundError as e:
            abort(404, message=str(e))
        except DatabaseError as e:
            abort(500, message=str(e))

    @ns.marshal_with(status_fields)
    @ns.expect(user_update_model, validate=True)
    @ns.doc('update_user', description='Met à jour un utilisateur')
    def put(self, id: str):
        """Met à jour un utilisateur avec validation automatique via @api.expect"""
        data = ns.payload  # Les données sont déjà validées par @api.expect
        name = data.get("name")
        email = data.get("email")
        
        # Vérification qu'au moins un champ est fourni
        if name is None and email is None:
            abort(400, message="Au moins un champ (name ou email) doit être fourni pour la mise à jour")
        
        try:
            update_user(id, name=name, email=email)
            return {"status": "updated"}, 200
        except InvalidUserIdError as e:
            abort(400, message=str(e))
        except UserNotFoundError as e:
            abort(404, message=str(e))
        except ValueError as e:
            abort(400, message=str(e))
        except DatabaseError as e:
            abort(500, message=str(e))


@ns.route('/<string:id>/tasks')
class UserTasksResource(Resource):
    @ns.marshal_with(paginated_tasks_fields)
    @ns.doc('get_user_tasks', description='Récupère les tâches d\'un utilisateur spécifique')
    def get(self, id: str):

        # Vérification que l'utilisateur existe d'abord
        try:
            users = get_all_users()
            user_exists = any(str(user.id) == id for user in users)
            if not user_exists:
                abort(404, message=f"Utilisateur avec l'ID '{id}' non trouvé")
        except DatabaseError as e:
            abort(500, message=str(e))
        
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
        
        # Récupération des tâches de l'utilisateur
        try:
            all_tasks = get_all_tasks(user_id=id)
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


def register_user_routes(api: Api) -> None:
    
    api.add_namespace(ns, path='/users')
