from flask_restx import fields
from .task_dto import task_fields


user_fields = {
    "id": fields.String,
    "name": fields.String,
    "email": fields.String,
}

# Champs pour un utilisateur avec ses tâches
user_with_tasks_fields = {
    "id": fields.String,
    "name": fields.String,
    "email": fields.String,
    "tasks": fields.List(fields.Nested(task_fields)),
}

# Champs pour la pagination des utilisateurs (avec tâches)
paginated_users_fields = {
    "items": fields.List(fields.Nested(user_with_tasks_fields)),
    "pagination": fields.Nested({
        "page": fields.Integer,
        "per_page": fields.Integer,
        "total": fields.Integer,
        "pages": fields.Integer,
        "has_next": fields.Boolean,
        "has_prev": fields.Boolean,
    }),
}

# Champs d'input pour la création d'utilisateur
user_input_fields = {
    "name": fields.String(required=True, description="Nom de l'utilisateur"),
    "email": fields.String(required=True, description="Email de l'utilisateur"),
}

# Champs d'input pour la mise à jour d'utilisateur
user_update_fields = {
    "name": fields.String(required=False, description="Nom de l'utilisateur (optionnel)"),
    "email": fields.String(required=False, description="Email de l'utilisateur (optionnel)"),
}
