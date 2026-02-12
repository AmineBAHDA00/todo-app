from flask import Flask
from flask_cors import CORS

from .mongoDB.db import init_db
from .routes import register_routes


def create_app() -> Flask:

    app = Flask(__name__)
    CORS(app)

    # Initialisation de la base de données
    init_db()

    # Enregistrement des routes
    register_routes(app)

    return app

