
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
