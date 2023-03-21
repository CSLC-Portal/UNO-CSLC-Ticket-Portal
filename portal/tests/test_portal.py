
from flask import Flask
from app.model import Ticket
from flask.testing import FlaskClient

import pytest

def test_index(client : FlaskClient):
    response = client.get('/')

    # Without authentication, expect a redirect to the login page
    assert '302' in response.status

def test_create_ticket(client : FlaskClient):
    response = client.get('/create-ticket')
    assert b'<h1>Create Ticket Form</h1>' in response.data

def test_open_tickets(client : FlaskClient, app : Flask):

    test_form_data = {
        'emailAdressField':'test@test.email',
        'firstNameField':'John',
        'lastNameField':'Doe',
        'courseField':'course1',
        'sectionField':'section1',
        'assignmentNameField':'assignment1',
        'specificQuestionField':'This is my question?',
        'problemTypeField':'type1',
    }

    response = client.post('/open-tickets', data=test_form_data)

    with app.app_context():
        assert b'John' in response.data
        assert Ticket.query.count() == 1
        assert Ticket.query.first().student_email == 'test@test.email'

def test_login(client : FlaskClient):
    response = client.get('/login')
    assert b'<h2>Login</h2>' in response.data

@pytest.mark.skip(reason='Need mockup response for microsoft auth')
def test_index_auth(client : FlaskClient):
    pass

@pytest.mark.skip(reason='Need mockup response for microsoft auth')
def test_login_auth(client : FlaskClient):
    pass

@pytest.mark.skip(reason='Need mockup response for microsoft auth')
def test_logout_auth(client : FlaskClient):
    pass
