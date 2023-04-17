
from flask import Flask
from app.model import Ticket
from flask.testing import FlaskClient

import pytest

def test_index_with_auth(create_auth_client):
    client = create_auth_client(name='John Smith')

    response = client.get('/')

    assert b'John Smith' in response.data

def test_create_ticket_get_with_auth(auth_client: FlaskClient):
    response = auth_client.get('/create-ticket')

    assert b'<h1>Create Ticket Form</h1>' in response.data

def test_create_ticket_post_with_auth(auth_client: FlaskClient, app: Flask):

    test_form_data = {
        'email':'test@test.email',
        'fullname':'John Doe',
        'course':'course1',
        'section':'section1',
        'assignment':'assignment1',
        'question':'This is my question?',
        'problem':'type1'
    }

    response = auth_client.post('/create-ticket', data=test_form_data)

    with app.app_context():
        assert Ticket.query.count() == 1

        ticket: Ticket = Ticket.query.first()
        assert ticket.student_email == 'test@test.email'
        assert ticket.student_name == 'John Doe'
        assert ticket.course == 'course1'
        assert ticket.section == 'section1'
        assert ticket.assignment_name == 'assignment1'
        assert ticket.specific_question == 'This is my question?'
        assert ticket.problem_type == 'type1'

    # Expect redirect back to index
    assert '302' in response.status
    assert b'href="/"' in response.data

def test_create_ticket_invalid_data(auth_client: FlaskClient, app: Flask):
    response = auth_client.post('/create-ticket', data={})

    with app.app_context():
        assert Ticket.query.count() == 0

    with auth_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not submit ticket, invalid data'

    assert '302' in response.status
    assert b'href="/"' in response.data

def test_logout_auth(auth_client: FlaskClient):
    response = auth_client.get('/logout')

    # We should be redirected to microsoft logout authority
    assert '302' in response.status
    assert b'logout' in response.data

@pytest.mark.skip(reason='Make test for adding tickets??')
def test_add_tickets(auth_client: FlaskClient):
    # ticket1 = m.Ticket('test@test.com','clayton safranek','data structures','101','assignment1','idk how to turn my computer on','big big problem',now(),m.Status.Open,m.Mode.InPerson)
    # ticket2 = m.Ticket('hellohello@test.com','john doe','basket weaving','101101','basket1','idk what a basket is','large problem',now(),m.Status.Claimed,m.Mode.InPerson)
    # ticket3 = m.Ticket('goodbye@test.com','jane smith','claymation','4000','sculpting2','idk what clay is','massive problem',now(),m.Status.Closed,m.Mode.Online)
    pass
