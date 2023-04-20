
from flask.testing import FlaskClient
import os

def test_index_no_auth(client: FlaskClient):
    response = client.get('/')

    # Without authentication, expect it to ask for login
    assert '200' in response.status
    assert b'Login' in response.data

    # Make sure the login URL is correct
    assert b'https://login.microsoftonline.com/common' in response.data

def test_create_ticket_no_auth(client: FlaskClient):
    response1 = client.get('/create-ticket')
    response2 = client.post('/create-ticket')

    # Without authentication, expect redirect to authority login
    assert '302' in response1.status
    assert '302' in response2.status

    # Make sure the login URL is correct
    assert b'https://login.microsoftonline.com/common' in response1.data
    assert b'https://login.microsoftonline.com/common' in response2.data

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
