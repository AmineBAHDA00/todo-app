import logging

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
from app.utils.dtos.user_dto import (
    user_fields,
    user_with_tasks_fields,
    paginated_users_fields,
    user_input_fields,
    user_update_fields,
)
from app.utils.dtos.task_dto import status_fields, paginated_tasks_fields

# Logger du module
logger = logging.getLogger(__name__)

# Namespace pour organiser les routes
ns = Namespace('users', description='Opérations sur les utilisateurs')

# Modèles pour la validation avec @api.expect (basés sur les DTO)
user_input_model = ns.model("UserInput", user_input_fields)
user_update_model = ns.model("UserUpdate", user_update_fields)


@ns.route('')
class UserListResource(Resource):
    @ns.marshal_with(paginated_users_fields)
    @ns.doc('list_users', description='Récupère la liste paginée des utilisateurs avec leurs tâches')
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
        
        # Récupération de tous les utilisateurs
        try:
            all_users = get_all_users()
        except DatabaseError:
            logger.exception("Erreur de base de données lors de la récupération des utilisateurs")
            abort(500, message="Une erreur interne est survenue lors de la récupération des utilisateurs.")
        except Exception:
            logger.exception("Erreur inattendue lors de la récupération des utilisateurs")
            abort(500, message="Une erreur inattendue est survenue lors de la récupération des utilisateurs.")
        
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
                user_dict = user.to_api()
                # Récupération des tâches de l'utilisateur
                user_tasks = get_all_tasks(user_id=str(user.id))
                user_dict["tasks"] = [task.to_api() for task in user_tasks]
                users_with_tasks.append(user_dict)
        except DatabaseError:
            logger.exception("Erreur de base de données lors de la récupération des tâches des utilisateurs")
            abort(500, message="Une erreur interne est survenue lors de la récupération des tâches des utilisateurs.")
        except Exception:
            logger.exception("Erreur inattendue lors de la récupération des tâches des utilisateurs")
            abort(500, message="Une erreur inattendue est survenue lors de la récupération des tâches des utilisateurs.")
        
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
        except DatabaseError:
            logger.exception("Erreur de base de données lors de la création d'un utilisateur")
            abort(500, message="Une erreur interne est survenue lors de la création de l'utilisateur.")
        except Exception:
            logger.exception("Erreur inattendue lors de la création d'un utilisateur")
            abort(500, message="Une erreur inattendue est survenue lors de la création de l'utilisateur.")


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
            user_dict = user.to_api()

            # Récupération des tâches de l'utilisateur
            user_tasks = get_all_tasks(user_id=str(user.id))
            user_dict["tasks"] = [task.to_api() for task in user_tasks]

            return user_dict
        except InvalidUserIdError as e:
            abort(400, message=str(e))
        except UserNotFoundError as e:
            abort(404, message=str(e))
        except DatabaseError:
            logger.exception("Erreur de base de données lors de la récupération d'un utilisateur")
            abort(500, message="Une erreur interne est survenue lors de la récupération de l'utilisateur.")
        except Exception:
            logger.exception("Erreur inattendue lors de la récupération d'un utilisateur")
            abort(500, message="Une erreur inattendue est survenue lors de la récupération de l'utilisateur.")

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
        except DatabaseError:
            logger.exception("Erreur de base de données lors de la suppression d'un utilisateur")
            abort(500, message="Une erreur interne est survenue lors de la suppression de l'utilisateur.")
        except Exception:
            logger.exception("Erreur inattendue lors de la suppression d'un utilisateur")
            abort(500, message="Une erreur inattendue est survenue lors de la suppression de l'utilisateur.")

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
        except DatabaseError:
            logger.exception("Erreur de base de données lors de la mise à jour d'un utilisateur")
            abort(500, message="Une erreur interne est survenue lors de la mise à jour de l'utilisateur.")
        except Exception:
            logger.exception("Erreur inattendue lors de la mise à jour d'un utilisateur")
            abort(500, message="Une erreur inattendue est survenue lors de la mise à jour de l'utilisateur.")


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
        except DatabaseError:
            logger.exception("Erreur de base de données lors de la vérification de l'existence d'un utilisateur")
            abort(500, message="Une erreur interne est survenue lors de la vérification de l'utilisateur.")
        
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
        
        # Récupération des tâches de l'utilisateur
        try:
            all_tasks = get_all_tasks(user_id=id)
        except DatabaseError:
            logger.exception("Erreur de base de données lors de la récupération des tâches d'un utilisateur")
            abort(500, message="Une erreur interne est survenue lors de la récupération des tâches de l'utilisateur.")
        except Exception:
            logger.exception("Erreur inattendue lors de la récupération des tâches d'un utilisateur")
            abort(500, message="Une erreur inattendue est survenue lors de la récupération des tâches de l'utilisateur.")
        
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
