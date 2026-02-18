from flask import Flask
from flask_cors import CORS
from flask_restx import Api

from .mongoDB.db import init_db


def create_app() -> Flask:

    # Création de l'application Flask
    app = Flask(__name__)
    
    # Activation de CORS pour permettre les requêtes depuis le frontend
    CORS(app)

    # Initialisation de la connexion MongoDB
    init_db()

    # Configuration de l'API Flask-RESTX (avec support de @api.expect)
    api = Api(app, doc='/swagger/', title='Todo API', description='API pour la gestion des tâches et utilisateurs')

    # Enregistrement de toutes les routes depuis task_resource.py
    from app.api.task_resource import register_routes
    register_routes(api)
    
    # Enregistrement de toutes les routes depuis user_resource.py
    from app.api.user_resource import register_user_routes
    register_user_routes(api)

    return app

