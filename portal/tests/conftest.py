from app import create_app
from flask import Flask

import pytest
import os

@pytest.fixture
def app():
    # Use a temporary database for testing
    os.environ['FLASK_SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

    app = create_app()

    yield app

@pytest.fixture
def client(app : Flask):
    return app.test_client()
