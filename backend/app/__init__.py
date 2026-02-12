from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from .mongoDB.db import init_db


def create_app() -> Flask:

    # Création de l'application Flask
    app = Flask(__name__)
    
    # Activation de CORS pour permettre les requêtes depuis le frontend
    CORS(app)

    # Initialisation de la connexion MongoDB
    init_db()

    # Configuration de l'API Flask-RESTful
    api = Api(app)

    # Enregistrement de toutes les routes depuis task_resource.py
    from app.api.task_resource import register_routes
    register_routes(api)

    return app

