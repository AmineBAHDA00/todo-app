from flask import Flask
from flask_cors import CORS

from .db import init_db


def create_app() -> Flask:

    # Création de l'application Flask
    app = Flask(__name__)

    # Activation de CORS pour permettre les requêtes depuis le frontend
    CORS(app)

    # Initialisation de la connexion MongoDB
    init_db()

    # Création et configuration de l'API Flask-RESTX (avec support de @api.expect)
    from app.api import create_api
    create_api(app)

    return app

