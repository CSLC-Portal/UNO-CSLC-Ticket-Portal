from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Query

from app.model import Permission
from app.model import User
from app.model import Course
from app.model import Semester
from app.model import Professor
from app.model import Section

def test_tutor_view_info(tutor_client: FlaskClient, app: Flask):
    response = tutor_client.get('/view-tutor-info')

    # expect OK response
    assert '200' in response.status
    assert b'Edit Tutor Information' in response.data

def test_tutor_toggle_working(tutor_client: FlaskClient, app: Flask):
    response = tutor_client.get('/view-tutor-info')

    # expect OK response
    assert '200' in response.status
    assert b'Edit Tutor Information' in response.data

    # make sure tutor is not working first
    with app.app_context():
        assert User.query.first().tutor_is_working == False

    # toggle working
    response = tutor_client.post('/toggle-working', data={'toggleWorkingID':'1'})
    assert '302' in response.status

    # check tutor status changed
    with app.app_context():
        assert User.query.first().tutor_is_working == True

def test_tutor_toggle_not_working(tutor_client: FlaskClient, app: Flask):
    response = tutor_client.get('/view-tutor-info')

    # expect OK response
    assert '200' in response.status
    assert b'Edit Tutor Information' in response.data

    # make sure tutor is not working first
    with app.app_context():
        User.query.first().tutor_is_working = True
        assert User.query.first().tutor_is_working == True

        # toggle working to not working
        response = tutor_client.post('/toggle-working', data={'toggleWorkingID':'1'})
        assert '302' in response.status

        # check tutor status changed
        assert User.query.first().tutor_is_working == False

def test_tutor_toggle_can_tutor_course(admin_client: FlaskClient, tutor_client: FlaskClient, app: Flask):
    data = {
        'courseDepartment': 'CSCI',
        'courseNumber': '1234',
        'courseName': 'Intro to Rizzing',
        'displayOnIndex': 'False'
    }
    response = admin_client.post('/admin/courses/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/courses"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Course.query.count() == 1

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1
        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'Course created successfully!'

    # test tutor claim course
    with app.app_context():
        assert User.query.first().courses == []
        # tutor said they can tutor a course
        response = tutor_client.post('/toggle-can-tutor', data={'toggleCanTutorID':'1'})
        assert '302' in response.status
        assert User.query.first().courses == [Course.query.first()]

def test_tutor_toggle_can_tutor_multiple_courses(admin_client: FlaskClient, tutor_client: FlaskClient, app: Flask):
    data = {
        'courseDepartment': 'CSCI',
        'courseNumber': '1234',
        'courseName': 'Intro to Rizzing',
        'displayOnIndex': 'False'
    }
    response = admin_client.post('/admin/courses/add', data=data)
    data = {
        'courseDepartment': 'CSCI',
        'courseNumber': '1111',
        'courseName': 'Intro to Razzling',
        'displayOnIndex': 'Truie'
    }
    response = admin_client.post('/admin/courses/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/courses"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Course.query.count() == 2

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 2
        (category, message) = flashes[1]
        assert category == 'success'
        assert message == 'Course created successfully!'

    # test tutor claim course
    with app.app_context():
        assert User.query.first().courses == []
        # tutor said they can tutor a course
        response = tutor_client.post('/toggle-can-tutor', data={'toggleCanTutorID':'1'})
        response = tutor_client.post('/toggle-can-tutor', data={'toggleCanTutorID':'2'})
        assert '302' in response.status
        assert len(User.query.first().courses) == 2

def test_tutor_toggle_can_not_tutor_course(admin_client: FlaskClient, tutor_client: FlaskClient, app: Flask):
    data = {
        'courseDepartment': 'CSCI',
        'courseNumber': '1234',
        'courseName': 'Intro to Rizzing',
        'displayOnIndex': 'False'
    }
    response = admin_client.post('/admin/courses/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/courses"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Course.query.count() == 1

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1
        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'Course created successfully!'

    # test tutor claim course
    with app.app_context():
        assert User.query.first().courses == []
        # tutor said they can tutor a course
        response = tutor_client.post('/toggle-can-tutor', data={'toggleCanTutorID':'1'})
        assert '302' in response.status
        assert User.query.first().courses == [Course.query.first()]
        # toggle course again to remove it from tutor list
        response = tutor_client.post('/toggle-can-tutor', data={'toggleCanTutorID':'1'})
        assert '302' in response.status
        assert User.query.first().courses == []
