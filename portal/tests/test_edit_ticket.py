from flask import Flask
from app.model import Ticket, Status, Mode, User
from flask.testing import FlaskClient
from app.extensions import db
from app.model import Permission

# TODO: Make sure the flashed messages are correct!

def test_edit_unauthenticated(client: FlaskClient):
    response = client.post('/edit-ticket')

    # Expect redirect to sign-in
    assert '302' in response.status
    assert b'https://login.microsoftonline.com/common' in response.data

def test_edit_insufficient_privileges_student(auth_client: FlaskClient):
    response = auth_client.post('/edit-ticket')

    # Expect redirect to index
    assert '302' in response.status
    assert b'href="/"' in response.data

def test_edit_admin(admin_client: FlaskClient):
    response = admin_client.post('/edit-ticket', data={})

    # Expect redirect to view tickets
    assert '302' in response.status
    assert b'href="/view-tickets"' in response.data

def test_edit_no_data(tutor_client: FlaskClient):
    response = tutor_client.post('/edit-ticket')

    # Expect redirect to view tickets
    assert '302' in response.status
    assert b'href="/view-tickets"' in response.data

def test_edit_course(tutor_client: FlaskClient, app: Flask):
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
    response1 = tutor_client.post('/create-ticket', data=ticket1)

    # make sure test ticket gets created correctly
    with app.app_context():
        assert '302' in response1.status
        assert Ticket.query.count() == 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.course == "course1"

    editData = {
        'ticketIDModal': '1',
        'courseField': 'This is the updated course'
    }
    response2 = tutor_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '302' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.course == "This is the updated course"

def test_edit_section(tutor_client: FlaskClient, app: Flask):
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
    response1 = tutor_client.post('/create-ticket', data=ticket1)

    # make sure test ticket gets created correctly
    with app.app_context():
        assert '302' in response1.status
        assert Ticket.query.count() == 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.section == "section1"

    editData = {
        'ticketIDModal': '1',
        'sectionField': 'NeW SeCtIoNNNNN'
    }
    response2 = tutor_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '302' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.section == "NeW SeCtIoNNNNN"

def test_edit_assignment(tutor_client: FlaskClient, app: Flask):
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
    response1 = tutor_client.post('/create-ticket', data=ticket1)

    # make sure test ticket gets created correctly
    with app.app_context():
        assert '302' in response1.status
        assert Ticket.query.count() == 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.assignment_name == "assignment1"

    editData = {
        'ticketIDModal': '1',
        'assignmentNameField': 'NeW Co0L Assignment'
    }
    response2 = tutor_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '302' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.assignment_name == "NeW Co0L Assignment"

def test_edit_specific_question(tutor_client: FlaskClient, app: Flask):
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
    response1 = tutor_client.post('/create-ticket', data=ticket1)

    # make sure test ticket gets created correctly
    with app.app_context():
        assert '302' in response1.status
        assert Ticket.query.count() == 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.specific_question == "This is my question?"

    editData = {
        'ticketIDModal': '1',
        'specificQuestionField': 'ThiS is ACCCtualy my QueStiIon...?'
    }
    response2 = tutor_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '302' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.specific_question == "ThiS is ACCCtualy my QueStiIon...?"

def test_edit_problem_type(tutor_client: FlaskClient, app: Flask):
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
    response1 = tutor_client.post('/create-ticket', data=ticket1)

    # make sure test ticket gets created correctly
    with app.app_context():
        assert '302' in response1.status
        assert Ticket.query.count() == 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.problem_type == "type1"

    editData = {
        'ticketIDModal': '1',
        'problemTypeField': 'NeW problem TYpe!!'
    }
    response2 = tutor_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '302' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.problem_type == "NeW problem TYpe!!"

def test_edit_tutor(tutor_client: FlaskClient, app: Flask):
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
    response1 = tutor_client.post('/create-ticket', data=ticket1)

    # make sure test ticket gets created correctly
    with app.app_context():
        assert '302' in response1.status
        assert Ticket.query.count() == 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        # no tutor has claimed ticket yet
        assert testTicket.tutor_id == None

    # claim the open ticket
    claimData = {
        'ticketID': '1',
        'action': 'Claim'
    }
    response2 = tutor_client.post('/update-ticket', data=claimData)

    # make sure that test ticket status = claimed
    with app.app_context():
        assert '302' in response2.status
        assert Ticket.query.first().status == Status.Claimed
        assert Ticket.query.filter_by(status = Status.Claimed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = Status.Open).count() != 1
        assert Ticket.query.filter_by(status = Status.Closed).count() != 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.tutor_id == 1 # this is current user

        # make new user and put in db - verify it got created
        tutor2 = User("oooooooooooooooiiiiddddd", Permission.Student, "Doctor", "Timothy Smith", False, False)
        tutor3 = User("12332DASDVncud543234!*$(", Permission.Student, "Mister", "John Doe", False, False)
        db.session.add(tutor2)
        db.session.add(tutor3)
        db.session.commit()

        # current user, tutor2, and tutor3 are all users in db
        students = User.query.filter(User.permission == Permission.Student)
        assert User.query.count() == 3
        assert students.count() == 2

    editData = {
        'ticketIDModal': '1',
        'primaryTutorInput': '2' # this is tutor2
    }
    response2 = tutor_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '302' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.tutor_id == 2 # this is tutor2
        assert testTicket.user.name == "Timothy Smith"

def test_edit_tutor_notes(tutor_client: FlaskClient, app: Flask):
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
    response1 = tutor_client.post('/create-ticket', data=ticket1)

    # make sure test ticket gets created correctly
    with app.app_context():
        assert '302' in response1.status
        assert Ticket.query.count() == 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.tutor_notes == ""

    editData = {
        'ticketIDModal': '1',
        'tutorNotes': 'TTEESSTT Tutor N0T3s!!'
    }
    response2 = tutor_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '302' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.tutor_notes == "TTEESSTT Tutor N0T3s!!"

def test_edit_was_successful(tutor_client: FlaskClient, app: Flask):
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
    response1 = tutor_client.post('/create-ticket', data=ticket1)

    # make sure test ticket gets created correctly
    with app.app_context():
        assert '302' in response1.status
        assert Ticket.query.count() == 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.successful_session == None

    editData = {
        'ticketIDModal': '1',
        'successfulSession': 'success'
    }
    response2 = tutor_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '302' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.successful_session == True

    # change the value back to false
        editData = {
        'ticketIDModal': '1',
        'successfulSession': None # this simulates an unchecked checkbox
    }
    response3 = tutor_client.post('/edit-ticket', data=editData)
    with app.app_context():
        assert '302' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.successful_session == False

def test_edit_multiple_attributes(tutor_client: FlaskClient, app: Flask):
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
    response1 = tutor_client.post('/create-ticket', data=ticket1)

    # make sure test ticket gets created correctly
    with app.app_context():
        assert '302' in response1.status
        assert Ticket.query.count() == 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.tutor_notes == ""

    editData = {
        'ticketIDModal': '1',
        'tutorNotes': 'TTEESSTT Tutor N0T3s!!'
    }
    response2 = tutor_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '302' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.tutor_notes == "TTEESSTT Tutor N0T3s!!"

# claim the open ticket
    claimData = {
        'ticketID': '1',
        'action': 'Claim'
    }
    response2 = tutor_client.post('/update-ticket', data=claimData)

    # make sure that test ticket status = claimed
    with app.app_context():
        assert '302' in response2.status
        assert Ticket.query.first().status == Status.Claimed
        assert Ticket.query.filter_by(status = Status.Claimed).count() == 1
        # check ticket is not in another category at the same time
        assert Ticket.query.filter_by(status = Status.Open).count() != 1
        assert Ticket.query.filter_by(status = Status.Closed).count() != 1
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.tutor_id == 1 # this is current user

    # make new user and put in db - verify it got created
    with app.app_context():
        tutor2 = User("oooooooooooooooiiiiddddd", Permission.Student, "Doctor", "Timothy Smith", False, False)
        tutor3 = User("12332DASDVncud543234!*$(", Permission.Student, "Mister", "John Doe", False, False)
        db.session.add(tutor2)
        db.session.add(tutor3)
        db.session.commit()
        # current user, tutor2, and tutor3 are all users in db
        students = User.query.filter(User.permission == Permission.Student)
        assert User.query.count() == 3
        assert students.count() == 2

    editData = {
        'ticketIDModal': '1',
        'primaryTutorInput': '2' # this is tutor2
    }
    response2 = tutor_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '302' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.tutor_id == 2 # this is tutor2
        assert testTicket.user.name == "Timothy Smith"

    editData = {
        'ticketIDModal': '1',
        'specificQuestionField': 'ThiS is ACCCtualy my QueStiIon...?'
    }
    response2 = tutor_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '302' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.specific_question == "ThiS is ACCCtualy my QueStiIon...?"

    editData = {
        'ticketIDModal': '1',
        'courseField': 'This is the updated course'
    }
    response2 = tutor_client.post('/edit-ticket', data=editData)

    # make sure test ticket gets updated correctly
    with app.app_context():
        assert '302' in response2.status
        testTicket = Ticket.query.filter_by(student_email="test@test.email").first()
        assert testTicket.course == "This is the updated course"
