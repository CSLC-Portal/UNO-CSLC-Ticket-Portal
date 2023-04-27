
from flask import Flask
from app.model import Ticket, Status, Mode
from flask.testing import FlaskClient

import pytest

def test_index_with_auth(create_auth_client):
    client = create_auth_client(name='John Smith')

    response = client.get('/')

    assert b'WELCOME TO THE UNO CSLC' in response.data

def test_create_ticket_get_with_auth(auth_client: FlaskClient):
    response = auth_client.get('/create-ticket')

    assert b'<h1>Create Ticket Form</h1>' in response.data

def test_logout_auth(auth_client: FlaskClient):
    response = auth_client.get('/logout')

    # We should be redirected to microsoft logout authority
    assert '302' in response.status
    assert b'logout' in response.data

def test_claim_open_ticket(auth_client: FlaskClient, app: Flask):
    # make a ticket
    ticket1 = {
        'email':'test@test.email',
        'fullname':'John Doe',
        'course':'course1',
        'section':'section1',
        'assignment':'assignment1',
        'question':'This is my question?',
        'problem':'type1',
        'mode': Mode.InPerson.value
    }
    response1 = auth_client.post('/create-ticket', data=ticket1)

    # make sure test ticket gets created
    with app.app_context():
        assert Ticket.query.count() == 1

    # claim open ticket
    claimData = {
        'ticketID': '1',
        'action': 'Claim'
    }
    response2 = auth_client.post('/update-ticket', data=claimData)

    # make sure that test ticket status = claimed
    with app.app_context():
        assert '200' in response2.status
        assert Ticket.query.first().status == Status.Claimed
        assert Ticket.query.filter_by(status = Status.Claimed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = Status.Open).count() != 1
        assert Ticket.query.filter_by(status = Status.Closed).count() != 1

def test_close_claimed_ticket(auth_client: FlaskClient, app: Flask):
    # make a ticket
    ticket1 = {
        'email':'test@test.email',
        'fullname':'John Doe',
        'course':'course1',
        'section':'section1',
        'assignment':'assignment1',
        'question':'This is my question?',
        'problem':'type1',
        'mode': Mode.InPerson.value
    }
    response1 = auth_client.post('/create-ticket', data=ticket1)

    # make sure test ticket gets created
    with app.app_context():
        assert Ticket.query.count() == 1

    # claim open ticket
    claimData = {
        'ticketID': '1',
        'action': 'Claim'
    }
    response2 = auth_client.post('/update-ticket', data=claimData)

    # make sure that test ticket status = claimed
    with app.app_context():
        assert '200' in response2.status
        assert Ticket.query.first().status == Status.Claimed
        assert Ticket.query.filter_by(status = Status.Claimed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = Status.Open).count() != 1
        assert Ticket.query.filter_by(status = Status.Closed).count() != 1

    # close claimed ticket
    closeData = {
        'ticketID': '1',
        'action': 'Close'
    }
    repsonse3 = auth_client.post('/update-ticket', data=closeData)

    # make sure that the test ticket status = closed
    with app.app_context():
        assert '200' in repsonse3.status
        assert Ticket.query.first().status == Status.Closed
        assert Ticket.query.filter_by(status = Status.Closed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = Status.Open).count() != 1
        assert Ticket.query.filter_by(status = Status.Claimed).count() != 1

def test_reopen_closed_ticket(auth_client: FlaskClient, app: Flask):
    # make a ticket
    ticket1 = {
        'email':'test@test.email',
        'fullname':'John Doe',
        'course':'course1',
        'section':'section1',
        'assignment':'assignment1',
        'question':'This is my question?',
        'problem':'type1',
        'mode': Mode.InPerson.value
    }
    response1 = auth_client.post('/create-ticket', data=ticket1)

    # make sure test ticket gets created
    with app.app_context():
        assert Ticket.query.count() == 1

    # claim open ticket
    claimData = {
        'ticketID': '1',
        'action': 'Claim'
    }
    response2 = auth_client.post('/update-ticket', data=claimData)

    # make sure that test ticket status = claimed
    with app.app_context():
        assert '200' in response2.status
        assert Ticket.query.first().status == Status.Claimed
        assert Ticket.query.filter_by(status = Status.Claimed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = Status.Open).count() != 1
        assert Ticket.query.filter_by(status = Status.Closed).count() != 1

    # close claimed ticket
    closeData = {
        'ticketID': '1',
        'action': 'Close'
    }
    repsonse3 = auth_client.post('/update-ticket', data=closeData)

    # make sure that the test ticket status = closed
    with app.app_context():
        assert '200' in repsonse3.status
        assert Ticket.query.first().status == Status.Closed
        assert Ticket.query.filter_by(status = Status.Closed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = Status.Open).count() != 1
        assert Ticket.query.filter_by(status = Status.Claimed).count() != 1

    # reopen closed ticket
    reopenData = {
        'ticketID': '1',
        'action': 'ReOpen'
    }
    response4 = auth_client.post('/update-ticket', data=reopenData)

    # make sure that the test ticket status is back to open
    with app.app_context():
        assert '200' in response4.status
        assert Ticket.query.first().status == Status.Open
        assert Ticket.query.filter_by(status = Status.Open).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = Status.Claimed).count() != 1
        assert Ticket.query.filter_by(status = Status.Closed).count() != 1

