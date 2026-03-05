from flask_restx import fields


task_fields = {
    "id": fields.String,
    "title": fields.String,
    "completed": fields.Boolean,
    "user_id": fields.String,
}

status_fields = {
    "status": fields.String,
}

# Champs pour la pagination
pagination_fields = {
    "page": fields.Integer,
    "per_page": fields.Integer,
    "total": fields.Integer,
    "pages": fields.Integer,
    "has_next": fields.Boolean,
    "has_prev": fields.Boolean,
}

# Structure de réponse paginée
paginated_tasks_fields = {
    "items": fields.List(fields.Nested(task_fields)),
    "pagination": fields.Nested(pagination_fields),
}

# Champs d'input pour la création de tâche (utilisés par @api.expect)
task_input_fields = {
    "title": fields.String(required=True, description="Titre de la tâche"),
    "user_id": fields.String(required=True, description="ID de l'utilisateur propriétaire"),
}

# Champs d'input pour la mise à jour de tâche
task_update_fields = {
    "completed": fields.Boolean(required=True, description="Statut de complétion de la tâche"),
}
