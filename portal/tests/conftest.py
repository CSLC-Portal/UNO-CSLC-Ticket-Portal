from app import create_app
from app import extensions
from flask import Flask

from app.model import db
from app.model import Permission
from app.model import ProblemType

from app.blueprints.admin import create_pseudo_super_user

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

    # NOTE: Here we add some default configs
    # TODO: This will be replaced by some default config for the app
    #       We should make the config available to the tests!
    #
    with app.app_context():
        db.session.add(ProblemType('This is the first problem type!'))
        db.session.add(ProblemType('This is the second problem type!'))
        db.session.commit()

    # We yield the app in case we later need to tear-down after each test
    yield app

@pytest.fixture
def client(app : Flask):
    """Provides a test flask client for sending http requests to the application."""

    return app.test_client()

@pytest.fixture
def create_auth_client(app : Flask):
    """Provides an factory function for creating an authenticated client."""

    # This factory function sets some parameters we can choose in the test
    def _factory(name = None, email = None, oid = None):

        # We make a new client that way we can have multiple, each with their own session
        # Using client() fixture would result in only one client being used for all create_auth_client()
        new_client = app.test_client()

        # Save previous values for future tests
        old_name = MockConfidentialClientApplication.MOCK_NAME
        old_email = MockConfidentialClientApplication.MOCK_EMAIL
        old_oid = MockConfidentialClientApplication.MOCK_OID

        if name is not None:
            MockConfidentialClientApplication.MOCK_NAME = name

        if email is not None:
            MockConfidentialClientApplication.MOCK_EMAIL = email

        if oid is not None:
            MockConfidentialClientApplication.MOCK_OID = oid

        # Login the client
        new_client.get(os.getenv('AAD_REDIRECT_PATH'))

        # Reapply previous values for future tests
        MockConfidentialClientApplication.MOCK_NAME = old_name
        MockConfidentialClientApplication.MOCK_EMAIL = old_email
        MockConfidentialClientApplication.MOCK_OID = old_oid
        return new_client

    return _factory

@pytest.fixture
def auth_client(create_auth_client):
    """Provides a default authenticated client."""

    return create_auth_client()

@pytest.fixture
def create_super_user(create_auth_client, app: Flask):
    def _factory(name = None, email = None, oid = None, permission = Permission.Admin):
        with app.app_context():
            create_pseudo_super_user(email, permission)

        return create_auth_client(name, email, oid)

    return _factory

@pytest.fixture
def tutor_client(create_super_user):
    return create_super_user(email='tutor@email.com', permission=Permission.Tutor)

@pytest.fixture
def admin_client(create_super_user):
    return create_super_user(email='admin@email.com', permission=Permission.Admin)

@pytest.fixture
def owner_client(create_super_user):
    return create_super_user(email='owner@email.com', permission=Permission.Owner)

@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Clean up sessions directory once all the tests are done."""

    def remove_sess_dir():
        shutil.rmtree('flask_session/')

    request.addfinalizer(remove_sess_dir)
