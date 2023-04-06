
from flask import Flask
from app.model import Ticket, Status, Mode
from flask.testing import FlaskClient
import datetime

import pytest

def test_index_with_auth(create_auth_client):
    client = create_auth_client(name='John Smith')

    response = client.get('/')

    assert b'John Smith' in response.data

def test_create_ticket_with_auth(auth_client: FlaskClient):
    response = auth_client.get('/create-ticket')

    assert b'<h1>Create Ticket Form</h1>' in response.data

def test_open_tickets_with_auth(auth_client: FlaskClient, app: Flask):

    test_form_data = {
        'emailAdressField':'test@test.email',
        'firstNameField':'John',
        'lastNameField':'Doe',
        'courseField':'course1',
        'sectionField':'section1',
        'assignmentNameField':'assignment1',
        'specificQuestionField':'This is my question?',
        'problemTypeField':'type1',
        'modeOfTicket':'InPerson'
    }

    response = auth_client.post('/open-tickets', data=test_form_data)

    with app.app_context():
        assert b'John' in response.data
        assert Ticket.query.count() == 1
        assert Ticket.query.first().student_email == 'test@test.email'

def test_logout_auth(auth_client: FlaskClient):
    response = auth_client.get('/logout')

    # We should be redirected to microsoft logout authority
    assert '302' in response.status
    assert b'logout' in response.data

def test_add_tickets(auth_client: FlaskClient, app: Flask):
    UTC = datetime.timezone.utc
    now = datetime.datetime.now(UTC)

    ticket1 = {
        'emailAdressField':'test@test.email',
        'firstNameField':'John',
        'lastNameField':'Doe',
        'courseField':'data structures',
        'sectionField':'section1',
        'assignmentNameField':'assignment1',
        'specificQuestionField':'This is my question?',
        'problemTypeField':'type1',
        'modeOfTicket':'InPerson'
    }
    ticket2 = {
        'emailAdressField':'test@test.email',
        'firstNameField':'Clayton',
        'lastNameField':'Safranek',
        'courseField':'underwater basket weaving',
        'sectionField':'section1',
        'assignmentNameField':'assignment1',
        'specificQuestionField':'What is your question?',
        'problemTypeField':'type1',
        'modeOfTicket':'Online'
    }
    response1 = auth_client.post('/open-tickets', data=ticket1)
    response2 = auth_client.post('/open-tickets', data=ticket2)

    with app.app_context():
        assert Ticket.query.count() == 2
