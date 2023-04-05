
from flask.testing import FlaskClient
import os

def test_index_no_auth(client: FlaskClient):
    response = client.get('/')

    # Without authentication, expect a redirect to the login page
    assert '302' in response.status
    assert b'/login' in response.data

def test_create_ticket_no_auth(client: FlaskClient):
    response = client.get('/create-ticket')

    # Without authentication, expect an authentication error
    assert '401' in response.status

def test_open_tickets_no_auth(client: FlaskClient):
    response = client.post('/open-tickets', data={})

    # Without authentication, expect an authentication error
    assert '401' in response.status

def test_logout_no_auth(client: FlaskClient):
    response = client.get('/logout', data={})

    # Without authentication, expect an authentication error
    assert '401' in response.status

def test_login_page(client : FlaskClient):
    response = client.get('/login')
    assert b'<h2>Login</h2>' in response.data

def test_mock_login(client: FlaskClient):
    response = client.get(os.getenv('AAD_REDIRECT_PATH'))

    # After successfully authenticating, redirect to index page
    assert '302' in response.status
