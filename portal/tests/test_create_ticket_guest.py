from flask import Flask
from flask.testing import FlaskClient

from app.model import Ticket
from app.model import Mode
from app.model import Course
from app.model import Section
from app.model import SectionMode

import pytest

def test_create_ticket_post_with_no_auth(client: FlaskClient, mock_courses, mock_sections, app: Flask):
    mock_courses(Course('CSCI', '1400', 'Intro to CS 1', False))
    mock_sections(Section('850', 'Mon', None, None, SectionMode.TotallyOnline, '1', None, None))

    test_form_data = {
        'email':'test@test.email',
        'fullname':'John Doe',
        'course':'1',
        'section':'1',
        'assignment':'assignment1',
        'question':'This is my question?',
        'problem':'1',
        'mode': Mode.InPerson.value
    }

    response = client.post('/create-ticket', data=test_form_data)

    with app.app_context():
        assert Ticket.query.count() == 1

        ticket: Ticket = Ticket.query.first()
        assert ticket.student_email == 'test@test.email'
        assert ticket.student_name == 'John Doe'
        assert ticket.course == '1'
        assert ticket.section == '1'
        assert ticket.assignment_name == 'assignment1'
        assert ticket.specific_question == 'This is my question?'
        assert ticket.problem_type == 1
        assert ticket.mode == Mode.InPerson

    with client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'Ticket created successfully!'

    # Expect redirect back to index
    assert '302' in response.status
    assert b'href="/"' in response.data

def test_create_ticket_no_data(client: FlaskClient, app: Flask):
    response = client.post('/create-ticket')

    with app.app_context():
        assert Ticket.query.count() == 0

    with client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not submit ticket, invalid data'

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/create-ticket"' in response.data

@pytest.fixture
def create_ticket_with_invalid_data(client: FlaskClient, mock_courses, mock_sections, app: Flask):
    mock_courses(Course('CSCI', '1400', 'Intro to CS 1', False))
    mock_sections(Section('850', 'Mon', None, None, SectionMode.TotallyOnline, '1', None, None))

    test_form_data = {
        'email':'test@test.email',
        'fullname':'John Doe',
        'course':'1',
        'section':'1',
        'assignment':'assignment1',
        'question':'This is my question?',
        'problem':'1',
        'mode': Mode.InPerson.value
    }

    def _factory(**kwargs):
        for key, val in kwargs.items():
            test_form_data[key] = val

        response = client.post('/create-ticket', data=test_form_data)

        with app.app_context():
            assert Ticket.query.count() == 0

        return response

    yield _factory

def test_create_ticket_empty_email(create_ticket_with_invalid_data, client: FlaskClient):
    response = create_ticket_with_invalid_data(email='')

    with client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not submit ticket, email must not be empty!'

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/create-ticket"' in response.data

def test_create_ticket_empty_name(create_ticket_with_invalid_data, client: FlaskClient):
    response = create_ticket_with_invalid_data(fullname='')

    with client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not submit ticket, name must not be empty!'

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/create-ticket"' in response.data

def test_create_ticket_empty_assignment(create_ticket_with_invalid_data, client: FlaskClient):
    response = create_ticket_with_invalid_data(assignment='')

    with client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not submit ticket, assignment name must not be empty!'

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/create-ticket"' in response.data

def test_create_ticket_empty_question(create_ticket_with_invalid_data, client: FlaskClient):
    response = create_ticket_with_invalid_data(question='')

    with client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not submit ticket, question must not be empty!'

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/create-ticket"' in response.data

def test_create_ticket_whitespace_email(create_ticket_with_invalid_data, client: FlaskClient):
    response = create_ticket_with_invalid_data(email='      \t')

    with client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not submit ticket, email must not be empty!'

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/create-ticket"' in response.data

def test_create_ticket_whitespace_name(create_ticket_with_invalid_data, client: FlaskClient):
    response = create_ticket_with_invalid_data(fullname='      \t')

    with client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not submit ticket, name must not be empty!'

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/create-ticket"' in response.data

def test_create_ticket_whitespace_assignment(create_ticket_with_invalid_data, client: FlaskClient):
    response = create_ticket_with_invalid_data(assignment='      \t')

    with client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not submit ticket, assignment name must not be empty!'

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/create-ticket"' in response.data

def test_create_ticket_whitespace_question(create_ticket_with_invalid_data, client: FlaskClient):
    response = create_ticket_with_invalid_data(question='      \t')

    with client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not submit ticket, question must not be empty!'

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/create-ticket"' in response.data

def test_create_ticket_invalid_mode(create_ticket_with_invalid_data, client: FlaskClient):
    response = create_ticket_with_invalid_data(mode='invalid')

    with client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not submit ticket, must select a valid mode!'

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/create-ticket"' in response.data
