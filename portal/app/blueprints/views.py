from flask import Blueprint
from flask import request
from flask import flash
from flask import url_for
from flask import redirect
from flask import render_template
from flask import jsonify

import json


from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from app.util import strip_or_none
from app.util import str_empty
from app.util import permission_required

from app.model import Ticket
from app.model import Mode
from app.model import Permission
from app.model import Message
from app.model import ProblemType
from app.model import Course
from app.model import Section
from app.model import User
from app import _read_in_config_data
from datetime import datetime

from app.extensions import db
from werkzeug.datastructures import ImmutableMultiDict

import sys

views = Blueprint('views', __name__)

# Temporary route to make a GET request to http://127.0.0.1:5000/ to create a new user
# It has already been migrated to next js and should not be used for anything other than local development
#
@views.route("/")
def index():
    """
    This index() funciton returns the main home page of the CSLC! It returns the render template for index.html. It also does
    a couple small queries for courses and messages to display on the home page.
    """
    toDisplay = Course.query.filter_by(on_display=True)
    messages = Message.query.filter(Message.start_date < datetime.now(), Message.end_date > datetime.now())

    # from flask_login import login_user
    # user = User.query.filter_by(email='email@email.com').first()

    # user = User('x', Permission.Owner, 'email@email.com', 'bruh', True, True)
    # db.session.add(user)
    # db.session.commit()
    # login_user(user)

    return render_template('index.html', messages=messages, OnDisplay=toDisplay)

@views.route("/api/home")
def api_home():
    toDisplay = Course.query.filter_by(on_display=True)
    messages = Message.query.filter(Message.start_date < datetime.now(), Message.end_date > datetime.now())
    
    config_data = _read_in_config_data()
    response = config_data
    
    response['updates'] = [{'id': message.id, 'message': message.message, 'start_date': message.start_date.timestamp(), 'end_date': message.end_date.timestamp()} for message in messages]

    response['availability'] = [{
        'id': course.id,
        'department': course.department,
        'number': course.number,
        'course_name': course.course_name,
        'tutors': [tutor.name for tutor in course.canTutors]
    } for course in toDisplay]

    return json.dumps(response)

@views.route("/api/current_user")
def get_current_user():    
    from flask_login import login_user
    user = User.query.filter_by(email='email@email.com').first()
    login_user(user)

    if current_user.is_authenticated:
        user_dict = {
            'id': current_user.id,
            'name': current_user.name,
            'email': current_user.email,
            'isAuthenticated': current_user.is_authenticated,
            'permission': str(current_user.permission)
        }

        return jsonify(user_dict)
    else:
        return jsonify({ 'isAuthenticated': False })

@views.route('/api/get-all-sections')
def get_all_sections():
    all_sections = Section.query.all()
    section_results = [{"id": section.id, "courseId": section.course_id, "sectionNumber": section.section_number } for section in all_sections]
    return json.dumps(section_results)

@views.route('/api/get-all-courses')
def get_all_courses():
    all_courses = Course.query.all()
    course_results = [{"id": course.id, "courseName": course.course_name } for course in all_courses]
    return json.dumps(course_results)

@views.route('/api/get-all-problem-types')
def get_all_problem_types():
    all_problem_types = ProblemType.query.all()
    problem_types = [{"id": problem_type.id, "type": problem_type.problem_type } for problem_type in all_problem_types]
    return json.dumps(problem_types)


@views.route('/api/create-ticket', methods=['POST', 'GET'])
def create_ticket():
    """
    Serves the HTTP route /create-ticket. Shows a ticket create form on GET request.
    Submits a ticket on POST request with a form containing the following fields:
    - email: Email address of user
    - fullname: Full name of user
    - course: Course relevant to the ticket submission
    - section: Section of course relevant to the ticket submission
    - assignment: Name of assignment relevant to the ticket submission
    - question: Detailed questions relevant to the ticket submission
    - problem: Type of problem needed help with
    - mode: Whether the student is online or in-person

    Then redirects back to the home page.

    Utilizes the flask funciton 'render_template' to render
    the passed in create-ticket.html template which is the form that students use to create/submit tickets.

    Student login is required to access this page.
    """
    print(request.form)
    ticket = _attempt_create_ticket(request.form)
    print(ticket)

    if ticket:
        try:
            db.session.add(ticket)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            return jsonify({ "success": False })
            # flash('Could not submit ticket, invalid data', category='error')

        except Exception as e:
            return jsonify({ "success": False })
            # flash('Could not submit ticket, unknown reason', category='error')
            # print(f'Failed to create ticket: {e}', file=sys.stderr)

        else:
            return jsonify({ "success": True })
            # flash('Ticket created successfully!', category='success')
            # return redirect(url_for('views.index'))

    return jsonify({ "success": False })#redirect(url_for('views.create_ticket'))

@views.route('/view-tickets')
@permission_required(Permission.Tutor)
def view_tickets():
    """
    Serves the HTTP route /view-tickets. This function queries the Tickets database and passes the result query
    to the front end to display all of the availabe tickets in the database.

    Utilizes the flask funciton 'render_template' to render the passed in view-tickets.html template which is
    used to display all tickets to tutors to be able to claim individual tickets.

    Student login is required to access this page.
    """
    tickets = Ticket.query.all()
    return render_template('view_tickets.html', tickets=tickets)

@views.route('/update-ticket', methods=["POST"])
@permission_required(Permission.Tutor)
def update_ticket():
    """
    This function handles the HTTP request when a tutor hits the claim, close, or reopen buttons on tickets
    :return: Render template to the original view-ticket.html page.
    """
    # get the tutors to display for edit ticket modal if the user presses it
    ticketID = request.form.get("ticketID")
    ticket: Ticket = Ticket.query.get(ticketID)

    # TODO: Check to make state is valid before changing it!!

    if ticket is None:
        flash('Could not update ticket status. Ticket not found in database.', category='error')

    elif request.form.get("action") == "Claim":
        ticket.claim(current_user)
        db.session.commit()
        flash('Ticket claimed!', category='info')

    elif request.form.get("action") == "Close":
        ticket.close()
        db.session.commit()
        flash('Ticket closed!', category='info')

    elif request.form.get("action") == "Open":
        ticket.reopen()
        db.session.commit()
        flash('Ticket opened!', category='info')

    else:
        flash('Did not change ticket status. Unknown action.', category='error')

    return redirect(url_for('views.view_tickets'))

@views.route('/edit-ticket', methods=["POST"])
@permission_required(Permission.Tutor)
def edit_ticket():
    """
    The funciton edit_ticket() houses all of the logic for a tutor to edit a seticketction in the database. When the HTTP
    route /edit-ticket is hit with a POST request, the data from the form is sent back and the appropriate logic is run
    to edit a ticket in the database.
    """
    # get ticket id back + current ticket
    ticketID = request.form.get("ticketIDModal")
    ticket = Ticket.query.get(ticketID)

    try:
        if ticket is not None:
            _attempt_edit_ticket(ticket)

        else:
            flash('Could not edit ticket. Ticket not found in database.', category='error')

    except IntegrityError:
        db.session.rollback()
        flash('Could not updated ticket, invalid data', category='error')

    except Exception as e:
        flash('Could not updated ticket, unknown reason', category='error')
        print(f'Failed to updated ticket: {e}', file=sys.stderr)

    else:
        flash('Ticket updated successfully!', category='success')

    return redirect(url_for('views.view_tickets'))

@views.route('/view-tutor-info', methods=["GET"])
@permission_required(Permission.Tutor)
def view_info():
    """
    The view_into() function is the main funciton that displays the info page for a tutor to edit tthier working status and
    also the different courses that they are able to tutor in. The HTTP route /view-tutor-info will render the template HTML
    "edit-tutor-info.html" on a GET request
    """
    # edit tutor activity status, and classes they can help with
    courses = Course.query.all()
    return render_template('edit-tutor-info.html', courses=courses)

@views.route('/toggle-working', methods=['POST'])
@permission_required(Permission.Tutor)
def toggle_working():
    """
    The toggle_working() function houses all of the logic for a tutor to toggle whether or not they are currently working in the CSLC.
    This is different form currently employed, this is basically a tutor "clocking in" or saying that they are available to tutor students.
    """
    user_id = request.form.get("toggleWorkingID")
    try:
        user: User = User.query.get(user_id)
        # reverse whatever value it currently has for display
        if user.tutor_is_working is True:
            user.tutor_is_working = False
        else:
            user.tutor_is_working = True
        print("Working: " + str(user.tutor_is_working))
        db.session.commit()

    except ValueError:
        flash('Could not toggle working status, input values invalid!', category='error')

    except IntegrityError:
        flash('Could not toggle working status, invalid data!', category='error')

    except Exception as e:
        flash('Could not toggle working status, unknown reason!', category='error')
        print(f'Could not toggle working status, {e}', file=sys.stderr)
    return redirect(url_for('views.view_info'))

@views.route('/toggle-can-tutor', methods=["POST"])
@permission_required(Permission.Tutor)
def toggle_can_tutor():
    """
    The toggle_can_tutor() funciton houses all the logic for tutors to specify what courses they are able to tutor or not.
    If a tutor is able to tutor a course they will toggle the button for each course and that will add it to their list of courses
    they are able to study. The join table can_tutor is utlizied in this funciton
    """
    course_id = request.form.get("toggleCanTutorID")
    user_id = current_user.id
    print("User ID: " + str(user_id))
    course = Course.query.filter_by(id=course_id).one_or_none()
    print("Course tutor says they can tutor: " + str(course))

    tutor = User.query.filter_by(id=user_id).one_or_none()
    print("Tutor: " + str(tutor))
    if course not in tutor.courses:
        tutor.courses.append(course)
    else:
        print("COURSE ALREADY IN LIST FOR TUTOR - REMOVING")
        tutor.courses.remove(course)
    print("Tutor Courses: " + str(tutor.courses))

    return redirect(url_for('views.view_info'))

# TODO: Use flask-wtf for form handling and validation
def _attempt_create_ticket(form: ImmutableMultiDict):
    """
    Given an HTML form as an ImmutableMultiDict, extracts, strips, and verifies the following values :
        - email: must be non-empty
        - fullname: must be non-empty
        - assignment: must be non-empty
        - question: must be non-empty
        - mode: must be valid model.Mode

        returns a Ticket object if values are valid, None otherwise.
    """

    # If the user is logged in, use their name and email
    if current_user.is_authenticated:
        email = current_user.email
        name = current_user.name

    # Otherwise get it from the form
    else:
        email = strip_or_none(form.get("email"))
        name = strip_or_none(form.get("fullname"))

    course_id = strip_or_none(form.get("course"))
    section_id = strip_or_none(form.get("section"))
    assignment = strip_or_none(form.get("assignment"))
    question = strip_or_none(form.get("question"))
    problem_id = strip_or_none(form.get("problem"))

    problem: ProblemType = ProblemType.query.get(problem_id)
    course: Course = Course.query.get(course_id)
    section: Section = Section.query.get(section_id)

    if str_empty(email):
        flash('Could not submit ticket, email must not be empty!', category='error')

    elif str_empty(name):
        flash('Could not submit ticket, name must not be empty!', category='error')

    elif str_empty(assignment):
        flash('Could not submit ticket, assignment name must not be empty!', category='error')

    elif str_empty(question):
        flash('Could not submit ticket, question must not be empty!', category='error')

    elif problem_id is not None and not problem:
        flash('Could not submit ticket, problem type is not valid!', category='error')

    elif course_id is not None and not course:
        flash('Could not submit ticket, course is not valid!', category='error')

    elif (section_id is not None and not section) or (course and section not in course.sections):
        flash('Could not submit ticket, section is not valid!', category='error')

    else:
        mode_val = strip_or_none(form.get("mode"))
        mode = None

        try:
            if mode_val:
                mode = Mode(int(mode_val))

        except ValueError:
            flash('Could not submit ticket, must select a valid mode!', category='error')

        else:
            return Ticket(email, name, course_id, section_id, assignment, question, problem_id, mode)

def _attempt_edit_ticket(ticket: Ticket):
    """
    This funciton takes in all of the data from the edit ticket form and sanitizes it and makes sure that it is valid data
    before editing the ticket
    """
    # TODO: Need to produce error messages!!

    course_id = strip_or_none(request.form.get("courseField"))
    section_id = strip_or_none(request.form.get("sectionField"))
    assignment = strip_or_none(request.form.get("assignmentNameField"))
    question = strip_or_none(request.form.get("specificQuestionField"))
    primaryTutor = strip_or_none(request.form.get("primaryTutorInput"))
    tutorNotes = strip_or_none(request.form.get("tutorNotes"))
    wasSuccessful = strip_or_none(request.form.get("successfulSession"))
    problem_id = strip_or_none(request.form.get("problemTypeField"))

    problem: ProblemType = ProblemType.query.get(problem_id)
    new_course: Course = Course.query.get(course_id)
    section: Section = Section.query.get(section_id)

    # Get the course of the current section
    current_course: Course = Course.query.get(ticket.course)

    # check for change in values from edit
    if course_id and new_course:
        # new info for course came back, update it for current ticket
        ticket.course = new_course.id
        ticket.section = new_course.sections[0].id if len(new_course.sections) > 0 else None
        current_course = new_course

    if section_id and section and section in current_course.sections:
        # new info for section came back, update it for current ticket
        ticket.section = section.id

    if assignment and assignment != ticket.assignment_name:
        # new info for assignment came back, update it for current ticket
        ticket.assignment_name = assignment

    if question and question != ticket.specific_question:
        # new info for question came back, update it for current ticket
        ticket.specific_question = question

    if problem:
        # new info for problem came back, update it for current ticket
        ticket.problem_type = problem_id

    if primaryTutor:
        # new info for primary tutor came back, update it for current ticket
        ticket.tutor_id = primaryTutor

    if tutorNotes:
        # new info for tutor notes came back, update it for current ticket
        ticket.tutor_notes = tutorNotes

    # new info for tutor notes came back, update it for current ticket
    ticket.successful_session = wasSuccessful is not None
    db.session.commit()
