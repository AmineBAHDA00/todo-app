from flask import Flask
from flask_cors import CORS
from .db import init_db


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Init database
    init_db()

    # Import et enregistrement des routes seulement après init_db
    from routes import register_routes
    register_routes(app)

    return app
