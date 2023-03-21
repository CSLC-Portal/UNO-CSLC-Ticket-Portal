from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from . import default_config

from time import sleep
from sys import stderr
import sys
import os

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

def setup_env(app: Flask):
    # Default config is always set to ensure app runs correctly
    app.config.from_object(default_config)

    # Override defaults with any configuration settings from the environment
    app.config.from_prefixed_env()

def create_db(app: Flask):
    db.init_app(app)

    # NOTE: Import model scripts here...
    from . import model

    # NOTE: From the MySQL docker image documentation:
    #
    #   "If there is no database initialized when the container starts, then a default database will be created.
    #   While this is the expected behavior, this means that it will not accept incoming connections until such initialization completes.
    #   This may cause issues when using automation tools, such as docker-compose, which start several containers simultaneously."
    #   ...
    #   "If the application you're trying to connect to MySQL does not handle MySQL downtime or waiting for MySQL to start gracefully,
    #   then putting a connect-retry loop before the service starts might be necessary."
    #

    killswitch = int(os.getenv('DATABASE_RECONNECT_ATTEMPTS', 15))
    cooldown = float(os.getenv('DATABASE_RECONNECT_COOLDOWN', 3))

    while killswitch >= 0:
        try:
            # Since SQLAlchemy 3.0+ create_all() requires an app context to run
            with app.app_context():
                db.create_all()

            # We succeeded! Break out of this loop
            print('Successfully connected to database server!')
            return

        except Exception:
            print(f'Failed to create database tables, will attempt to reconnect in {cooldown:.2f} seconds...', file=stderr)
            killswitch -= 1
            sleep(cooldown)
            continue

    print('Could not connect to or find database server, ensure it is running!', file=stderr)
    sys.exit(-1)
