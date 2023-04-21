
from flask import Flask
from app.model import Ticket, Status, Mode
from flask.testing import FlaskClient
import datetime
from app import model as m
from app.extensions import db

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
        assert Ticket.query.first().status == m.Status.Claimed
        assert Ticket.query.filter_by(status = m.Status.Claimed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = m.Status.Open).count() != 1
        assert Ticket.query.filter_by(status = m.Status.Closed).count() != 1

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
        assert Ticket.query.first().status == m.Status.Claimed
        assert Ticket.query.filter_by(status = m.Status.Claimed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = m.Status.Open).count() != 1
        assert Ticket.query.filter_by(status = m.Status.Closed).count() != 1

    # close claimed ticket
    closeData = {
        'ticketID': '1',
        'action': 'Close'
    }
    repsonse3 = auth_client.post('/update-ticket', data=closeData)

    # make sure that the test ticket status = closed
    with app.app_context():
        assert '200' in repsonse3.status
        assert Ticket.query.first().status == m.Status.Closed
        assert Ticket.query.filter_by(status = m.Status.Closed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = m.Status.Open).count() != 1
        assert Ticket.query.filter_by(status = m.Status.Claimed).count() != 1

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
        assert Ticket.query.first().status == m.Status.Claimed
        assert Ticket.query.filter_by(status = m.Status.Claimed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = m.Status.Open).count() != 1
        assert Ticket.query.filter_by(status = m.Status.Closed).count() != 1

    # close claimed ticket
    closeData = {
        'ticketID': '1',
        'action': 'Close'
    }
    repsonse3 = auth_client.post('/update-ticket', data=closeData)

    # make sure that the test ticket status = closed
    with app.app_context():
        assert '200' in repsonse3.status
        assert Ticket.query.first().status == m.Status.Closed
        assert Ticket.query.filter_by(status = m.Status.Closed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = m.Status.Open).count() != 1
        assert Ticket.query.filter_by(status = m.Status.Claimed).count() != 1

    # reopen closed ticket
    reopenData = {
        'ticketID': '1',
        'action': 'ReOpen'
    }
    response4 = auth_client.post('/update-ticket', data=reopenData)

    # make sure that the test ticket status is back to open
    with app.app_context():
        assert '200' in response4.status
        assert Ticket.query.first().status == m.Status.Open
        assert Ticket.query.filter_by(status = m.Status.Open).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = m.Status.Claimed).count() != 1
        assert Ticket.query.filter_by(status = m.Status.Closed).count() != 1

def test_edit_course(auth_client: FlaskClient, app: Flask):
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

    # make sure test ticket gets created correctly
    with app.app_context():
        assert '200' in response1.status
        assert Ticket.query.count() == 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.course == "data structures"

    editData = {
        'ticketIDModal': '1',
        'courseField': 'This is the updated course'
    }
    response2 = auth_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '200' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.course == "This is the updated course"

def test_edit_section(auth_client: FlaskClient, app: Flask):
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

    # make sure test ticket gets created correctly
    with app.app_context():
        assert '200' in response1.status
        assert Ticket.query.count() == 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.section == "section1"

    editData = {
        'ticketIDModal': '1',
        'sectionField': 'NeW SeCtIoNNNNN'
    }
    response2 = auth_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '200' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.section == "NeW SeCtIoNNNNN"

def test_edit_assignment(auth_client: FlaskClient, app: Flask):
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

    # make sure test ticket gets created correctly
    with app.app_context():
        assert '200' in response1.status
        assert Ticket.query.count() == 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.assignment_name == "assignment1"

    editData = {
        'ticketIDModal': '1',
        'assignmentNameField': 'NeW Co0L Assignment'
    }
    response2 = auth_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '200' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.assignment_name == "NeW Co0L Assignment"

def test_edit_specific_question(auth_client: FlaskClient, app: Flask):
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

    # make sure test ticket gets created correctly
    with app.app_context():
        assert '200' in response1.status
        assert Ticket.query.count() == 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.specific_question == "This is my question?"

    editData = {
        'ticketIDModal': '1',
        'specificQuestionField': 'ThiS is ACCCtualy my QueStiIon...?'
    }
    response2 = auth_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '200' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.specific_question == "ThiS is ACCCtualy my QueStiIon...?"

def test_edit_problem_type(auth_client: FlaskClient, app: Flask):
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

    # make sure test ticket gets created correctly
    with app.app_context():
        assert '200' in response1.status
        assert Ticket.query.count() == 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.problem_type == "type1"

    editData = {
        'ticketIDModal': '1',
        'problemTypeField': 'NeW problem TYpe!!'
    }
    response2 = auth_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '200' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.problem_type == "NeW problem TYpe!!"

def test_edit_tutor(auth_client: FlaskClient, app: Flask):
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

    # make sure test ticket gets created correctly
    with app.app_context():
        assert '200' in response1.status
        assert Ticket.query.count() == 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        # no tutor has claimed ticket yet
        assert testTicket.tutor_id == None

    # claim the open ticket
    claimData = {
        'ticketID': '1',
        'action': 'Claim'
    }
    response2 = auth_client.post('/update-ticket', data=claimData)

    # make sure that test ticket status = claimed
    with app.app_context():
        assert '200' in response2.status
        assert Ticket.query.first().status == m.Status.Claimed
        assert Ticket.query.filter_by(status = m.Status.Claimed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = m.Status.Open).count() != 1
        assert Ticket.query.filter_by(status = m.Status.Closed).count() != 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.tutor_id == 1 # this is current user

    # make new user and put in db - verify it got created
    with app.app_context():
        tutor2 = m.User("oooooooooooooooiiiiddddd", 1, "Doctor", "Timothy Smith", False, False)
        tutor3 = m.User("12332DASDVncud543234!*$(", 1, "Mister", "John Doe", False, False)
        db.session.add(tutor2)
        db.session.add(tutor3)
        db.session.commit()
        # current user, tutor2, and tutor3 are all users in db
        assert m.User.query.count() == 3
        # tutor2 and tutor3 only users with perm >= 1
        assert m.User.query.filter(m.User.permission_level >= 1).count() == 2

    editData = {
        'ticketIDModal': '1',
        'primaryTutorInput': '2' # this is tutor2
    }
    response2 = auth_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '200' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.tutor_id == 2 # this is tutor2
        assert testTicket.user.user_name == "Timothy Smith"

def test_edit_tutor_notes(auth_client: FlaskClient, app: Flask):
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

    # make sure test ticket gets created correctly
    with app.app_context():
        assert '200' in response1.status
        assert Ticket.query.count() == 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.tutor_notes == None

    editData = {
        'ticketIDModal': '1',
        'tutorNotes': 'TTEESSTT Tutor N0T3s!!'
    }
    response2 = auth_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '200' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.tutor_notes == "TTEESSTT Tutor N0T3s!!"

def test_edit_was_successful(auth_client: FlaskClient, app: Flask):
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

    # make sure test ticket gets created correctly
    with app.app_context():
        assert '200' in response1.status
        assert Ticket.query.count() == 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.successful_session == None

    editData = {
        'ticketIDModal': '1',
        'successfulSession': 'success'
    }
    response2 = auth_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '200' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.successful_session == True

    # change the value back to false
        editData = {
        'ticketIDModal': '1',
        'successfulSession': None # this simulates an unchecked checkbox
    }
    response3 = auth_client.post('/edit-ticket', data=editData)
    with app.app_context():
        assert '200' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.successful_session == False

def test_edit_multiple_attributes(auth_client: FlaskClient, app: Flask):
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

    # make sure test ticket gets created correctly
    with app.app_context():
        assert '200' in response1.status
        assert Ticket.query.count() == 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.tutor_notes == None

    editData = {
        'ticketIDModal': '1',
        'tutorNotes': 'TTEESSTT Tutor N0T3s!!'
    }
    response2 = auth_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '200' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.tutor_notes == "TTEESSTT Tutor N0T3s!!"

# claim the open ticket
    claimData = {
        'ticketID': '1',
        'action': 'Claim'
    }
    response2 = auth_client.post('/update-ticket', data=claimData)

    # make sure that test ticket status = claimed
    with app.app_context():
        assert '200' in response2.status
        assert Ticket.query.first().status == m.Status.Claimed
        assert Ticket.query.filter_by(status = m.Status.Claimed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = m.Status.Open).count() != 1
        assert Ticket.query.filter_by(status = m.Status.Closed).count() != 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.tutor_id == 1 # this is current user

    # make new user and put in db - verify it got created
    with app.app_context():
        tutor2 = m.User("oooooooooooooooiiiiddddd", 1, "Doctor", "Timothy Smith", False, False)
        tutor3 = m.User("12332DASDVncud543234!*$(", 1, "Mister", "John Doe", False, False)
        db.session.add(tutor2)
        db.session.add(tutor3)
        db.session.commit()
        # current user, tutor2, and tutor3 are all users in db
        assert m.User.query.count() == 3
        # tutor2 and tutor3 only users with perm >= 1
        assert m.User.query.filter(m.User.permission_level >= 1).count() == 2

    editData = {
        'ticketIDModal': '1',
        'primaryTutorInput': '2' # this is tutor2
    }
    response2 = auth_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '200' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.tutor_id == 2 # this is tutor2
        assert testTicket.user.user_name == "Timothy Smith"

    editData = {
        'ticketIDModal': '1',
        'specificQuestionField': 'ThiS is ACCCtualy my QueStiIon...?'
    }
    response2 = auth_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '200' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.specific_question == "ThiS is ACCCtualy my QueStiIon...?"

    editData = {
        'ticketIDModal': '1',
        'courseField': 'This is the updated course'
    }
    response2 = auth_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '200' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.course == "This is the updated course"
