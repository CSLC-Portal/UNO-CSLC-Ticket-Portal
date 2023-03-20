
from flask import Flask
from app.model import Ticket
from flask.testing import FlaskClient

def test_index(client : FlaskClient):
    response = client.get('/')
    assert response.data == b'Future site of the CSLC Tutoring Portal!'

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

