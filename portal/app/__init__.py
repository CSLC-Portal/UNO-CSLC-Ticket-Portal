from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from .extensions import db
from .extensions import sess
from .extensions import login_manager
from flask_login import current_user
from . import default_config

from time import sleep
from sys import stderr
import sys
import os

# NOTE: DO NOT change the name of 'create_app()', it is used by gunicorn and flask
def create_app():
    app = Flask(__name__)

    # Tell Flask it is behind a proxy, for accurate result when using url_for with external = True
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Make trailing slashes optional
    app.url_map.strict_slashes = False

    _setup_env(app)
    db.init_app(app)
    sess.init_app(app)
    login_manager.init_app(app)

    _create_db_models(app)
    _register_blueprints(app)

    app.jinja_env.globals['user'] = current_user
    return app

def _setup_env(app: Flask):
    # Default config is always set to ensure app runs correctly
    app.config.from_object(default_config)

    # Override defaults with any configuration settings from the environment
    app.config.from_prefixed_env()

def _register_blueprints(app: Flask):

    # We need to import blueprints to register them
    from .blueprints.views import views
    from .blueprints.auth import auth
    from .blueprints.admin import admin

    app.register_blueprint(views)
    app.register_blueprint(auth)
    app.register_blueprint(admin)

def _create_db_models(app: Flask):
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
