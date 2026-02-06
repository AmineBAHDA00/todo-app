from flask import Flask
from flask_cors import CORS
from .db import init_db

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Init database
    init_db()

    # Register routes
    from routes.task_routes import task_bp
    app.register_blueprint(task_bp)

    return app
