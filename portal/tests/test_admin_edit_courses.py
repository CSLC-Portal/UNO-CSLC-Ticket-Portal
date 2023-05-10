
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Query

from app.model import Permission
from app.model import User
from app.model import Course
from app.model import Semester
from app.model import Professor
from app.model import Section
from app.model import Season

def test_admin_edit_course(admin_client: FlaskClient, app: Flask):
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

    # edit course
    data = {
    'courseID': '1',
    'updateCourseDept': 'CSCI',
    'updateCourseNum': '6969',
    'updateCourseName': 'New Name'
    }
    response = admin_client.post('/admin/courses/edit', data=data)
    assert '302' in response.status

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 2
        (category, message) = flashes[1]
        assert category == 'success'
        assert message == 'Course updated successfully!'

def test_admin_edit_course_no_change(admin_client: FlaskClient, app: Flask):
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

    # edit course
    data = {
    'courseID': '1',
    'updateCourseDept': 'CSCI',
    'updateCourseNum': '1234',
    'updateCourseName': 'Intro to Rizzing'
    }
    response = admin_client.post('/admin/courses/edit', data=data)
    assert '302' in response.status

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 2
        (category, message) = flashes[1]
        assert category == 'message'
        assert message == 'No updates to course, attributes remain the same.'

def test_admin_toggle_course(admin_client: FlaskClient, app: Flask):
    data = {
        'courseDepartment': 'CSCI',
        'courseNumber': '1234',
        'courseName': 'Intro to Rizzing',
        'displayOnIndex': False
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

    # edit course
    data = {
    'toggleID': '1',
    }
    response = admin_client.post('/admin/courses/toggle-display', data=data)
    assert '302' in response.status

    with app.app_context():
        assert Course.query.filter_by(on_display = False).count() == 1

def test_admin_edit_semester(admin_client: FlaskClient, app: Flask):
    data = {
        'yearInput': '2020',
        'seasonInput': 'Fall',
        'startDate': '2023-05-17',
        'endDate': '2023-05-17'
    }
    response = admin_client.post('/admin/semesters/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/semesters"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Semester.query.count() == 1

    data = {
        'semesterID': '1',
        'yearUpdate': '2022',
        'seasonUpdate': 'Spring',
        'updateStartDate': '2023-05-17',
        'updateEndDate': '2023-05-17'
    }
    response = admin_client.post('/admin/semesters/edit', data=data)
    assert '302' in response.status
    with app.app_context():
        assert Semester.query.filter_by(year = 2022).count() == 1
        assert Semester.query.filter_by(season = Season.Spring).count() == 1

def test_admin_edit_semester_no_change(admin_client: FlaskClient, app: Flask):
    data = {
        'yearInput': '2020',
        'seasonInput': 'Fall',
        'startDate': '2023-05-17',
        'endDate': '2023-05-17'
    }
    response = admin_client.post('/admin/semesters/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/semesters"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Semester.query.count() == 1

    data = {
        'semesterID': '1',
        'yearUpdate': '2020',
        'seasonUpdate': 'Fall',
        'updateStartDate': '2023-05-17',
        'updateEndDate': '2023-05-17'
    }
    response = admin_client.post('/admin/semesters/edit', data=data)
    assert '302' in response.status
    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 2
        (category, message) = flashes[1]
        assert category == 'message'
        assert message == 'No updates to semester, attributes remain the same.'

def test_admin_edit_professor(admin_client: FlaskClient, app: Flask):
    data = {
        'firstNameInput': 'Billy',
        'lastNameInput': 'Bob'
    }
    response = admin_client.post('/admin/professors/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/professors"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Professor.query.count() == 1

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1
        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'Professor added successfully!'
    data = {
        'professorID': '1',
        'fnameUpdate': 'Billy',
        'lnameUpdate': 'Betty'}
    response = admin_client.post('/admin/professors/edit', data=data)
    assert '302' in response.status
    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 2
        (category, message) = flashes[1]
        assert category == 'success'
        assert message == 'Professor updated successfully!'

def test_admin_edit_professor_no_change(admin_client: FlaskClient, app: Flask):
    data = {
        'firstNameInput': 'Billy',
        'lastNameInput': 'Bob'
    }
    response = admin_client.post('/admin/professors/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/professors"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Professor.query.count() == 1

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1
        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'Professor added successfully!'
    data = {
        'professorID': '1',
        'fnameUpdate': 'Billy',
        'lnameUpdate': 'Bob'}
    response = admin_client.post('/admin/professors/edit', data=data)
    assert '302' in response.status
    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 2
        (category, message) = flashes[1]
        assert category == 'message'
        assert message == 'No updates to professor, attributes remain the same.'

def test_admin_edit_section(admin_client: FlaskClient, app: Flask):
    # make semester
    data = {
        'yearInput': '2020',
        'seasonInput': 'Fall',
        'startDate': '2023-05-24',
        'endDate': '2023-05-17'
    }
    response = admin_client.post('/admin/semesters/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/semesters"' in response.data
    with app.app_context():
        assert Semester.query.count() == 1

    # make course
    data = {
        'courseDepartment': 'CSCI',
        'courseNumber': '1234',
        'courseName': 'Intro to Rizzing',
        'displayOnIndex': 'False'
    }
    response = admin_client.post('/admin/courses/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/courses"' in response.data
    with app.app_context():
        assert Course.query.count() == 1

    # make prof
    data = {
        'firstNameInput': 'Billy',
        'lastNameInput': 'Bob'
    }
    response = admin_client.post('/admin/professors/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/professors"' in response.data
    with app.app_context():
        assert Professor.query.count() == 1

    data = {
        'semesterInput': '1',
        'courseInput': '1',
        'sectionNumberInput': '1212',
        'mode': 'InPerson',
        'mondayTime': 'monday',
        'tuesdayTime': '',
        'wednesdayTime': 'wednesday',
        'thursdayTime': '',
        'fridayTime': 'friday',
        'sectionStartTime': '22:00',
        'sectionEndTime': '14:00',
        'professorInput': '1'
    }
    response = admin_client.post('/admin/sections/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/sections"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Section.query.count() == 1

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 4
        (category, message) = flashes[3]
        assert category == 'success'
        assert message == 'Section added successfully!'

    data = {
        'sectionID': '1',
        'semesterUpdate': '1',
        'updateCourse': '1',
        'updateSectionNum': '1212',
        'updateMode': 'Remote',
        'updateMon': 'monday',
        'updateTue': 'tuesday',
        'updateWed': 'wednesday',
        'updateThu': '',
        'updateFri': 'friday',
        'updateStart': '18:00',
        'updateEnd': '06:00',
        'updateProf': '1'
    }
    response = admin_client.post('/admin/sections/edit', data=data)
    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 5
        (category, message) = flashes[4]
        assert category == 'success'
        assert message == 'Section updated successfully!'

def test_admin_edit_section_no_change(admin_client: FlaskClient, app: Flask):
    # make semester
    data = {
        'yearInput': '2020',
        'seasonInput': 'Fall',
        'startDate': '2023-05-24',
        'endDate': '2023-05-17'
    }
    response = admin_client.post('/admin/semesters/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/semesters"' in response.data
    with app.app_context():
        assert Semester.query.count() == 1

    # make course
    data = {
        'courseDepartment': 'CSCI',
        'courseNumber': '1234',
        'courseName': 'Intro to Rizzing',
        'displayOnIndex': 'False'
    }
    response = admin_client.post('/admin/courses/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/courses"' in response.data
    with app.app_context():
        assert Course.query.count() == 1

    # make prof
    data = {
        'firstNameInput': 'Billy',
        'lastNameInput': 'Bob'
    }
    response = admin_client.post('/admin/professors/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/professors"' in response.data
    with app.app_context():
        assert Professor.query.count() == 1

    data = {
        'semesterInput': '1',
        'courseInput': '1',
        'sectionNumberInput': '1212',
        'mode': 'InPerson',
        'mondayTime': 'monday',
        'tuesdayTime': '',
        'wednesdayTime': 'wednesday',
        'thursdayTime': '',
        'fridayTime': 'friday',
        'sectionStartTime': '22:00',
        'sectionEndTime': '14:00',
        'professorInput': '1'
    }
    response = admin_client.post('/admin/sections/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/sections"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Section.query.count() == 1

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 4
        (category, message) = flashes[3]
        assert category == 'success'
        assert message == 'Section added successfully!'

    data = {
        'sectionID': '1',
        'semesterUpdate': '1',
        'updateCourse': '1',
        'updateSectionNum': '1212',
        'updateMode': 'InPerson',
        'updateMon': 'monday',
        'updateTue': '',
        'updateWed': 'wednesday',
        'updateThu': '',
        'updateFri': 'friday',
        'updateStart': '22:00',
        'updateEnd': '14:00',
        'updateProf': '1'
    }
    response = admin_client.post('/admin/sections/edit', data=data)
    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 5
        (category, message) = flashes[4]
        assert category == 'message'
        assert message == 'No updates to section, attributes remain the same.'




