from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Query

from app.model import Permission
from app.model import User
from app.model import Course
from app.model import Semester
from app.model import Professor
from app.model import Section

def test_admin_hit_courses_page(admin_client: FlaskClient, app: Flask):
    response = admin_client.get('/admin/courses/')
    assert '200' in response.status

def test_admin_hit_course_sections_page(admin_client: FlaskClient, app: Flask):
    response = admin_client.get('/admin/sections/')
    assert '200' in response.status

def test_admin_hit_courses_page(admin_client: FlaskClient, app: Flask):
    response = admin_client.get('/admin/semesters/')
    assert '200' in response.status

def test_admin_hit_courses_page(admin_client: FlaskClient, app: Flask):
    response = admin_client.get('/admin/professors/')
    assert '200' in response.status

def test_admin_add_course(admin_client: FlaskClient, app: Flask):
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

def test_admin_add_course_empty_dept(admin_client: FlaskClient, app: Flask):
    data = {
        'courseDepartment': '    ',
        'courseNumber': '1234',
        'courseName': 'Intro to Rizzing',
        'displayOnIndex': 'False'
    }
    response = admin_client.post('/admin/courses/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/courses"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Course.query.count() == 0

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1
        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not create course, course department must not be empty!'

def test_admin_add_course_empty_num(admin_client: FlaskClient, app: Flask):
    data = {
        'courseDepartment': 'CSCI',
        'courseNumber': '   ',
        'courseName': 'Intro to Rizzing',
        'displayOnIndex': 'False'
    }
    response = admin_client.post('/admin/courses/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/courses"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Course.query.count() == 0

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1
        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not create course, course number must not be empty!'

def test_admin_add_course_empty_name(admin_client: FlaskClient, app: Flask):
    data = {
        'courseDepartment': 'CSCI',
        'courseNumber': '1234',
        'courseName': '   ',
        'displayOnIndex': 'True'
    }
    response = admin_client.post('/admin/courses/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/courses"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Course.query.count() == 0

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1
        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not create course, course name must not be empty!'

def test_admin_add_course_existing(admin_client: FlaskClient, app: Flask):
    data = {
        'courseDepartment': 'CSCI',
        'courseNumber': '1234',
        'courseName': 'New Course',
        'displayOnIndex': 'True'
    }
    response = admin_client.post('/admin/courses/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/courses"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Course.query.count() == 1

    # post exact same data
    response = admin_client.post('/admin/courses/add', data=data)
    with app.app_context():
        assert Course.query.count() == 1
    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 2
        (category, message) = flashes[1]
        assert category == 'error'
        assert message == "Course already exists in database!"

def test_admin_add_semester(admin_client: FlaskClient, app: Flask):
    data = {
        'yearInput': '2020',
        'seasonInput': 'Fall',
        'startDate': '2023-05-24',
        'endDate': '2023-05-17'
    }
    response = admin_client.post('/admin/semesters/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/semesters"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Semester.query.count() == 1

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1
        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'Semester created successfully!'

def test_admin_add_semester_empty_year(admin_client: FlaskClient, app: Flask):
    data = {
        'yearInput': '   ',
        'seasonInput': 'Fall',
        'startDate': '2023-05-24',
        'endDate': '2023-05-17'
    }
    response = admin_client.post('/admin/semesters/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/semesters"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Semester.query.count() == 0

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1
        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not create semester, year must not be empty!'

def test_admin_add_semester_empty_season(admin_client: FlaskClient, app: Flask):
    data = {
        'yearInput': '2020',
        'seasonInput': '   ',
        'startDate': '2023-05-24',
        'endDate': '2023-05-17'
    }
    response = admin_client.post('/admin/semesters/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/semesters"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Semester.query.count() == 0

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1
        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not create semester, season must not be empty!'

def test_admin_add_semester_empty_start_date(admin_client: FlaskClient, app: Flask):
    data = {
        'yearInput': '2020',
        'seasonInput': 'Fall',
        'startDate': '   ',
        'endDate': '2023-05-17'
    }
    response = admin_client.post('/admin/semesters/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/semesters"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Semester.query.count() == 0

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1
        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not create semester, start date must not be empty!'

def test_admin_add_semester_empty_end_date(admin_client: FlaskClient, app: Flask):
    data = {
        'yearInput': '2020',
        'seasonInput': 'Fall',
        'startDate': '2023-05-17',
        'endDate': '    '
    }
    response = admin_client.post('/admin/semesters/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/semesters"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Semester.query.count() == 0

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1
        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not create semester, end date must not be empty!'

def test_admin_add_semester_wack_year(admin_client: FlaskClient, app: Flask):
    data = {
        'yearInput': '20',
        'seasonInput': 'Fall',
        'startDate': '2023-05-17',
        'endDate': '2023-05-17'
    }
    response = admin_client.post('/admin/semesters/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/semesters"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Semester.query.count() == 0

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1
        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not create semester, please enter valid year in the format YYYY!'

def test_admin_add_semester_existing(admin_client: FlaskClient, app: Flask):
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

    # post exact same data
    response = admin_client.post('/admin/semesters/add', data=data)
    with app.app_context():
        assert Semester.query.count() == 1
    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 2
        (category, message) = flashes[1]
        assert category == 'error'
        assert message == "Semester 'Fall 2020' already exists in database!"

def test_admin_add_professor(admin_client: FlaskClient, app: Flask):
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

def test_admin_add_professor_empty_fname(admin_client: FlaskClient, app: Flask):
    data = {
        'firstNameInput': '   ',
        'lastNameInput': 'Bob'
    }
    response = admin_client.post('/admin/professors/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/professors"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Professor.query.count() == 0

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1
        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not add professor, first name must not be empty!'

def test_admin_add_professor_empty_lname(admin_client: FlaskClient, app: Flask):
    data = {
        'firstNameInput': 'Billy',
        'lastNameInput': '   '
    }
    response = admin_client.post('/admin/professors/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/professors"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Professor.query.count() == 0

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1
        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not add professor, last name must not be empty!'

def test_admin_add_professor_existing(admin_client: FlaskClient, app: Flask):
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

    # post exact same data
    response = admin_client.post('/admin/professors/add', data=data)
    with app.app_context():
        assert Professor.query.count() == 1
    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 2
        (category, message) = flashes[1]
        assert category == 'error'
        assert message == "Professor 'Billy Bob' already exists in database!"

def test_admin_add_section(admin_client: FlaskClient, app: Flask):
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

def test_admin_add_section_empty_days_inperson(admin_client: FlaskClient, app: Flask):
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
        'mondayTime': None,
        'tuesdayTime': None,
        'wednesdayTime': None,
        'thursdayTime': None,
        'fridayTime': None,
        'sectionStartTime': '22:00',
        'sectionEndTime': '14:00',
        'professorInput': '1'
    }
    response = admin_client.post('/admin/sections/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/sections"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Section.query.count() == 0

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 4
        (category, message) = flashes[3]
        assert category == 'error'
        assert message == 'Could not create section, must provide atleast one day of the week for section if mode is InPerson!'

def test_admin_add_section_empty_days_remote(admin_client: FlaskClient, app: Flask):
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
        'mode': 'Remote',
        'mondayTime': None,
        'tuesdayTime': None,
        'wednesdayTime': None,
        'thursdayTime': None,
        'fridayTime': None,
        'sectionStartTime': '22:00',
        'sectionEndTime': '14:00',
        'professorInput': '1'
    }
    response = admin_client.post('/admin/sections/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/sections"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Section.query.count() == 0

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 4
        (category, message) = flashes[3]
        assert category == 'error'
        assert message == 'Could not create section, must provide atleast one day of the week for section if mode is Remote!'

def test_admin_add_section_empty_start_time_remote(admin_client: FlaskClient, app: Flask):
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
        'mode': 'Remote',
        'mondayTime': 'monday',
        'tuesdayTime': None,
        'wednesdayTime': None,
        'thursdayTime': None,
        'fridayTime': None,
        'sectionStartTime': '',
        'sectionEndTime': '14:00',
        'professorInput': '1'
    }
    response = admin_client.post('/admin/sections/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/sections"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Section.query.count() == 0

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 4
        (category, message) = flashes[3]
        assert category == 'error'
        assert message == "Could not create section, must provide both start and end time for section if mode is Remote!"

def test_admin_add_section_empty_start_time_inperson(admin_client: FlaskClient, app: Flask):
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
        'tuesdayTime': None,
        'wednesdayTime': None,
        'thursdayTime': None,
        'fridayTime': None,
        'sectionStartTime': '',
        'sectionEndTime': '14:00',
        'professorInput': '1'
    }
    response = admin_client.post('/admin/sections/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/sections"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Section.query.count() == 0

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 4
        (category, message) = flashes[3]
        assert category == 'error'
        assert message == "Could not create section, must provide both start and end time for section if mode is InPerson!"

def test_admin_add_section_empty_end_time_remote(admin_client: FlaskClient, app: Flask):
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
        'mode': 'Remote',
        'mondayTime': 'monday',
        'tuesdayTime': None,
        'wednesdayTime': None,
        'thursdayTime': None,
        'fridayTime': None,
        'sectionStartTime': '14:00',
        'sectionEndTime': '',
        'professorInput': '1'
    }
    response = admin_client.post('/admin/sections/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/sections"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Section.query.count() == 0

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 4
        (category, message) = flashes[3]
        assert category == 'error'
        assert message == "Could not create section, must provide both start and end time for section if mode is Remote!"

def test_admin_add_section_empty_end_time_inperson(admin_client: FlaskClient, app: Flask):
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
        'mode': 'Remote',
        'mondayTime': 'monday',
        'tuesdayTime': None,
        'wednesdayTime': None,
        'thursdayTime': None,
        'fridayTime': None,
        'sectionStartTime': '14:00',
        'sectionEndTime': '',
        'professorInput': '1'
    }
    response = admin_client.post('/admin/sections/add', data=data)

    assert '302' in response.status
    assert b'href="/admin/sections"' in response.data

    # query db make sure course made it in
    with app.app_context():
        assert Section.query.count() == 0

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 4
        (category, message) = flashes[3]
        assert category == 'error'
        assert message == "Could not create section, must provide both start and end time for section if mode is Remote!"
