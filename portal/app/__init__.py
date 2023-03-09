from flask import Flask
from . import default_config

# NOTE: DO NOT change the name of 'create_app()', it is used by gunicorn
def create_app(name : str):
    new_app = Flask(name)

    # Default config is always set to ensure app runs correctly
    new_app.config.from_object(default_config)

    # Override defaults with any configuration settings from the environment
    new_app.config.from_prefixed_env()

    return new_app

app = create_app(__name__)

from app import views
