
from flask.testing import FlaskClient

import os

# TODO: Need to test more invalid input (e.g. long usernames, emails, etc.) break the database!

def test_index_no_auth(client: FlaskClient):
    response = client.get('/')

    # Without authentication, expect it to ask for login
    assert '200' in response.status
    assert b'Login' in response.data

    # Make sure the login URL is correct
    assert b'https://login.microsoftonline.com/common' in response.data

def test_logout_no_auth(client: FlaskClient):
    response = client.get('/logout', data={})

    # Without authentication, expect redirect to authority login
    assert '302' in response.status

    # Make sure the login URL is correct
    assert b'https://login.microsoftonline.com/common' in response.data

def test_mock_login(client: FlaskClient):
    response = client.get(os.getenv('AAD_REDIRECT_PATH'))

    # After successfully authenticating, redirect to index page
    assert '302' in response.status

def test_index_with_auth(create_auth_client):
    client = create_auth_client(name='John Smith')

    response = client.get('/')

    assert b'WELCOME TO THE UNO CSLC' in response.data

def test_create_ticket_get_with_auth(auth_client: FlaskClient):
    response = auth_client.get('/create-ticket')

    assert b'<h1>Create Ticket Form</h1>' in response.data

def test_logout_with_auth(auth_client: FlaskClient):
    response = auth_client.get('/logout')

    # We should be redirected to microsoft logout authority
    assert '302' in response.status
    assert b'logout' in response.data

