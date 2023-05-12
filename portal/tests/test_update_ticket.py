from flask import Flask

from app.model import Ticket
from app.model import Status
from app.model import Course
from app.model import Section
from app.model import SectionMode
from app.model import Mode

from flask.testing import FlaskClient

def test_claim_open_ticket(tutor_client: FlaskClient, mock_courses, mock_sections, app: Flask):
    mock_courses(Course('CSCI', '1400', 'Intro to CS 1', False))
    mock_sections(Section('850', 'Mon', None, None, SectionMode.TotallyOnline, '1', None, None))

    # make a ticket
    ticket1 = {
        'email':'test@test.email',
        'fullname':'John Doe',
        'course':'1',
        'section':'1',
        'assignment':'assignment1',
        'question':'This is my question?',
        'problem':'1',
        'mode': Mode.InPerson.value
    }
    tutor_client.post('/create-ticket', data=ticket1)

    # make sure test ticket gets created
    with app.app_context():
        assert Ticket.query.count() == 1

    # claim open ticket
    claimData = {
        'ticketID': '1',
        'action': 'Claim'
    }
    response = tutor_client.post('/update-ticket', data=claimData)

    # make sure that test ticket status = claimed
    with app.app_context():
        assert '302' in response.status
        assert Ticket.query.first().status == Status.Claimed
        assert Ticket.query.filter_by(status = Status.Claimed).count() == 1

        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = Status.Open).count() != 1
        assert Ticket.query.filter_by(status = Status.Closed).count() != 1

def test_close_claimed_ticket(tutor_client: FlaskClient, mock_courses, mock_sections, app: Flask):
    mock_courses(Course('CSCI', '1400', 'Intro to CS 1', False))
    mock_sections(Section('850', 'Mon', None, None, SectionMode.TotallyOnline, '1', None, None))

    # make a ticket
    ticket1 = {
        'email':'test@test.email',
        'fullname':'John Doe',
        'course':'1',
        'section':'1',
        'assignment':'assignment1',
        'question':'This is my question?',
        'problem':'1',
        'mode': Mode.InPerson.value
    }
    tutor_client.post('/create-ticket', data=ticket1)

    # make sure test ticket gets created
    with app.app_context():
        assert Ticket.query.count() == 1

    # claim open ticket
    claimData = {
        'ticketID': '1',
        'action': 'Claim'
    }
    response = tutor_client.post('/update-ticket', data=claimData)

    # make sure that test ticket status = claimed
    with app.app_context():
        assert '302' in response.status
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
    repsonse3 = tutor_client.post('/update-ticket', data=closeData)

    # make sure that the test ticket status = closed
    with app.app_context():
        assert '302' in repsonse3.status
        assert Ticket.query.first().status == Status.Closed
        assert Ticket.query.filter_by(status = Status.Closed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = Status.Open).count() != 1
        assert Ticket.query.filter_by(status = Status.Claimed).count() != 1

def test_reopen_closed_ticket(tutor_client: FlaskClient, mock_courses, mock_sections, app: Flask):
    mock_courses(Course('CSCI', '1400', 'Intro to CS 1', False))
    mock_sections(Section('850', 'Mon', None, None, SectionMode.TotallyOnline, '1', None, None))

    # make a ticket
    ticket1 = {
        'email':'test@test.email',
        'fullname':'John Doe',
        'course':'1',
        'section':'1',
        'assignment':'assignment1',
        'question':'This is my question?',
        'problem':'1',
        'mode': Mode.InPerson.value
    }
    tutor_client.post('/create-ticket', data=ticket1)

    # make sure test ticket gets created
    with app.app_context():
        assert Ticket.query.count() == 1

    # claim open ticket
    claimData = {
        'ticketID': '1',
        'action': 'Claim'
    }
    response = tutor_client.post('/update-ticket', data=claimData)

    # make sure that test ticket status = claimed
    with app.app_context():
        assert '302' in response.status
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
    repsonse3 = tutor_client.post('/update-ticket', data=closeData)

    # make sure that the test ticket status = closed
    with app.app_context():
        assert '302' in repsonse3.status
        assert Ticket.query.first().status == Status.Closed
        assert Ticket.query.filter_by(status = Status.Closed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = Status.Open).count() != 1
        assert Ticket.query.filter_by(status = Status.Claimed).count() != 1

    # reopen closed ticket
    reopenData = {
        'ticketID': '1',
        'action': 'Open'
    }
    response4 = tutor_client.post('/update-ticket', data=reopenData)

    # make sure that the test ticket status is back to open
    with app.app_context():
        assert '302' in response4.status
        assert Ticket.query.first().status == Status.Open
        assert Ticket.query.filter_by(status = Status.Open).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = Status.Claimed).count() != 1
        assert Ticket.query.filter_by(status = Status.Closed).count() != 1

def test_close_open_ticket(tutor_client: FlaskClient, mock_courses, mock_sections, app: Flask):
    mock_courses(Course('CSCI', '1400', 'Intro to CS 1', False))
    mock_sections(Section('850', 'Mon', None, None, SectionMode.TotallyOnline, '1', None, None))

    # make a ticket
    ticket1 = {
        'email':'test@test.email',
        'fullname':'John Doe',
        'course':'1',
        'section':'1',
        'assignment':'assignment1',
        'question':'This is my question?',
        'problem':'1',
        'mode': Mode.InPerson.value
    }
    tutor_client.post('/create-ticket', data=ticket1)

    # make sure test ticket gets created
    with app.app_context():
        assert Ticket.query.count() == 1

    # close open ticket
    response = tutor_client.post('/update-ticket', data={ 'ticketID': '1', 'action': 'Close' })

    # make sure that test ticket status = claimed
    with app.app_context():
        assert '302' in response.status
        assert Ticket.query.first().status == Status.Closed
        assert Ticket.query.filter_by(status = Status.Closed).count() == 1
