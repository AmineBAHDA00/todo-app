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
