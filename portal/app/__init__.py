from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

from . import default_config

db = SQLAlchemy()

# NOTE: DO NOT change the name of 'create_app()', it is used by gunicorn and flask
def create_app():
    app = Flask(__name__)

    setup_env(app)

    # We need to import blueprints and register them
    from .views import views
    app.register_blueprint(views)

    create_db(app)

    return app

def setup_env(app : Flask):
    # Default config is always set to ensure app runs correctly
    app.config.from_object(default_config)

    # Override defaults with any configuration settings from the environment
    app.config.from_prefixed_env()

def create_db(app : Flask):
    db.init_app(app)

    # Since SQLAlchemy 3.0+ create_all() requires an app context to run
    with app.app_context():
        db.create_all()
