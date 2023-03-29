from app import create_app
from flask import Flask

import pytest
import os
import shutil

@pytest.fixture
def app():
    """Creates and configures a debug flask app."""

    # Obviously set debugging and testing flags
    os.environ['FLASK_DEBUG'] = 'True'
    os.environ['FLASK_TESTING'] = 'True'

    # Use a temporary database for testing
    os.environ['FLASK_SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

    # Well unfortunately it seems there is a bug in Flask-Session where the database instance
    # Cannot be reused, we'll need to automatically delete this folder from disk once tests are done
    os.environ['FLASK_SESSION_TYPE'] = 'filesystem'

    # Set the required azure app directory authentication env variables
    os.environ['AAD_AUTHORITY'] = 'https://login.microsoftonline.com/common'
    os.environ['AAD_CLIENT_ID'] = 'DummyAppID'
    os.environ['AAD_CLIENT_SECRET'] = 'FakeClientSecret'
    os.environ['AAD_REDIRECT_PATH'] = '/getAToken'

    app = create_app()

    # We yield the app in case we later need to tear-down after each test
    yield app

@pytest.fixture
def client(app : Flask):
    """Provides a test flask client for sending http requests to the application."""

    return app.test_client()

@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Clean up sessions directory once all the tests are done."""

    def remove_sess_dir():
        shutil.rmtree('flask_session/')

    request.addfinalizer(remove_sess_dir)
