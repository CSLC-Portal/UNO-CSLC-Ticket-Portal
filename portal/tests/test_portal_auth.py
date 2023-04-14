
from flask import Flask
from app.model import Ticket, Status, Mode
from flask.testing import FlaskClient
import datetime
from app import model as m

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

def test_claim_open_ticket(auth_client: FlaskClient, app: Flask):
    # make a ticket
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
    response1 = auth_client.post('/open-tickets', data=ticket1)

    # make sure test ticket gets created
    with app.app_context():
        assert '200' in response1.status
        assert Ticket.query.count() == 1

    # claim open ticket
    claimData = {
        'action': 'Claim'
    }
    response2 = auth_client.post('/update-ticket/1', data=claimData)

    # make sure that test ticket status = claimed
    with app.app_context():
        assert '200' in response2.status
        print("REPONSE 2: " + str(response2))
        assert Ticket.query.first().status == m.Status.Claimed
        assert Ticket.query.filter_by(status = m.Status.Claimed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = m.Status.Open).count() != 1
        assert Ticket.query.filter_by(status = m.Status.Closed).count() != 1

def test_close_claimed_ticket(auth_client: FlaskClient, app: Flask):
    # make a ticket
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
    response1 = auth_client.post('/open-tickets', data=ticket1)

    # make sure test ticket gets created
    with app.app_context():
        assert '200' in response1.status
        assert Ticket.query.count() == 1

    # claim open ticket
    claimData = {
        'action': 'Claim'
    }
    response2 = auth_client.post('/update-ticket/1', data=claimData)

    # make sure that test ticket status = claimed
    with app.app_context():
        assert '200' in response2.status
        print("REPONSE 2: " + str(response2))
        assert Ticket.query.first().status == m.Status.Claimed
        assert Ticket.query.filter_by(status = m.Status.Claimed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = m.Status.Open).count() != 1
        assert Ticket.query.filter_by(status = m.Status.Closed).count() != 1

    # close claimed ticket
    closeData = {
        'action': 'Close'
    }
    repsonse3 = auth_client.post('/update-ticket/1', data=closeData)

    # make sure that the test ticket status = closed
    with app.app_context():
        assert '200' in response2.status
        print("REPONSE 3: " + str(response2))
        assert Ticket.query.first().status == m.Status.Closed
        assert Ticket.query.filter_by(status = m.Status.Closed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = m.Status.Open).count() != 1
        assert Ticket.query.filter_by(status = m.Status.Claimed).count() != 1

def test_reopen_closed_ticket(auth_client: FlaskClient, app: Flask):
    # make a ticket
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
    response1 = auth_client.post('/open-tickets', data=ticket1)

    # make sure test ticket gets created
    with app.app_context():
        assert '200' in response1.status
        assert Ticket.query.count() == 1

    # claim open ticket
    claimData = {
        'action': 'Claim'
    }
    response2 = auth_client.post('/update-ticket/1', data=claimData)

    # make sure that test ticket status = claimed
    with app.app_context():
        assert '200' in response2.status
        print("REPONSE 2: " + str(response2))
        assert Ticket.query.first().status == m.Status.Claimed
        assert Ticket.query.filter_by(status = m.Status.Claimed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = m.Status.Open).count() != 1
        assert Ticket.query.filter_by(status = m.Status.Closed).count() != 1

    # close claimed ticket
    closeData = {
        'action': 'Close'
    }
    repsonse3 = auth_client.post('/update-ticket/1', data=closeData)

    # make sure that the test ticket status = closed
    with app.app_context():
        assert '200' in response2.status
        print("REPONSE 3: " + str(response2))
        assert Ticket.query.first().status == m.Status.Closed
        assert Ticket.query.filter_by(status = m.Status.Closed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = m.Status.Open).count() != 1
        assert Ticket.query.filter_by(status = m.Status.Claimed).count() != 1

    # reopen closed ticket
    reopenData = {
        'action': 'ReOpen'
    }
    response4 = auth_client.post('/update-ticket/1', data=reopenData)

    # make sure that the test ticket status is back to open
    with app.app_context():
        assert '200' in response2.status
        print("REPONSE 3: " + str(response2))
        assert Ticket.query.first().status == m.Status.Open
        assert Ticket.query.filter_by(status = m.Status.Open).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = m.Status.Claimed).count() != 1
        assert Ticket.query.filter_by(status = m.Status.Closed).count() != 1
