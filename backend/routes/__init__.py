from .task_routes import task_bp

__all__ = ["task_bp", "register_routes"]


def register_routes(app, url_prefix: str = "") -> None:
    """
    Enregistre tous les blueprints de routes sur l'application Flask.
    """
    app.register_blueprint(task_bp, url_prefix=url_prefix)

