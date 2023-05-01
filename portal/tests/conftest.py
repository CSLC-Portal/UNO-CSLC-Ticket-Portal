from app import create_app
from app import extensions
from flask import Flask

from flask.testing import FlaskClient
from app.model import Permission
from app.blueprints.admin import create_pseudo_user

import pytest
import os
import shutil

from . import MockConfidentialClientApplication

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

    # NOTE: For mocking purposes we don't use MSAL's actual confidential client application
    extensions.auth_app_type = MockConfidentialClientApplication

    app = create_app()

    # We yield the app in case we later need to tear-down after each test
    yield app

@pytest.fixture
def client(app : Flask):
    """Provides a test flask client for sending http requests to the application."""

    return app.test_client()

@pytest.fixture
def create_auth_client(client: FlaskClient):
    """Provides an factory function for creating an authenticated client."""

    # This factory function sets some parameters we can choose in the test
    def _factory(name = None, email = None, oid = None):
        if name is not None:
            MockConfidentialClientApplication.MOCK_NAME = name

        if email is not None:
            MockConfidentialClientApplication.MOCK_EMAIL = email

        if oid is not None:
            MockConfidentialClientApplication.MOCK_OID = oid

        client.get(os.getenv('AAD_REDIRECT_PATH'))

        return client

    return _factory

@pytest.fixture
def auth_client(create_auth_client):
    """Provides a default authenticated client."""

    return create_auth_client()

@pytest.fixture
def tutor_client(create_auth_client, app: Flask):
    with app.app_context():
        create_pseudo_user('tutor@email.com', Permission.Tutor)

    return create_auth_client(email = 'tutor@email.com')

@pytest.fixture
def admin_client(create_auth_client, app: Flask):
    with app.app_context():
        create_pseudo_user('admin@email.com', Permission.Admin)

    return create_auth_client(email = 'admin@email.com')

@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Clean up sessions directory once all the tests are done."""

    def remove_sess_dir():
        shutil.rmtree('flask_session/')

    request.addfinalizer(remove_sess_dir)
