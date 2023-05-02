from flask import Blueprint
from flask import request
from flask import flash
from flask import url_for
from flask import redirect
from flask import render_template

from flask_login import login_required
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from app import model as m
from app.model import Ticket
from app.model import Mode
from app.model import Status
from app.model import User
from app.model import Courses
from app.model import Semesters

from datetime import datetime, date
from datetime import timedelta

from app.extensions import db
from werkzeug.datastructures import ImmutableMultiDict

import sys
import re

views = Blueprint('views', __name__)

@views.route('/create-ticket', methods=['POST', 'GET'])
@login_required
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
    if request.method == 'GET':
        # Render create-ticket template if GET request or if there was an error in submission data
        return render_template('create-ticket.html', Mode=Mode, user=current_user)

    ticket = _attempt_create_ticket(request.form)

    if ticket:
        try:
            db.session.add(ticket)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash('Could not submit ticket, invalid data', category='error')

        except Exception as e:
            flash('Could not submit ticket, unknown reason', category='error')
            print(f'Failed to create ticket: {e}', file=sys.stderr)

        else:
            flash('Ticket created successfully!', category='success')
            return redirect(url_for('auth.index'))

    return redirect(url_for('views.create_ticket'))

@views.route('/view-tickets')
@login_required
def view_tickets():
    """
    Serves the HTTP route /view-tickets. This function queries the Tickets database and passes the result query
    to the front end to display all of the availabe tickets in the database.

    Utilizes the flask funciton 'render_template' to render the passed in view-tickets.html template which is
    used to display all tickets to tutors to be able to claim individual tickets.

    Student login is required to access this page.
    """
    tickets = m.Ticket.query.all()  # .filter(_now() - Ticket.time_created).total_seconds()/(60*60) < 24)

    # Get the user permission level here BEFORE attempting to load view-tickets page
    user_level = current_user.permission_level
    if (user_level < 2):
        flash('Insufficient permission level to view tickets', category='error')
        return redirect(url_for('auth.index'))

    return render_template('view_tickets.html', Status=Status, user=current_user, tickets=tickets)

@views.route('/update-ticket', methods=["GET", "POST"])
@login_required
def update_ticket():
    """
    This function handles the HTTP request when a tutor hits the claim, close, or reopen buttons on tickets
    :return: Render template to the original view-ticket.html page.
    """
    # get the tutors to display for edit ticket modal if the user presses it
    tutors = m.User.query.filter(m.User.permission_level >= 1)
    tickets = m.Ticket.query.all()  # .filter(_now() - Ticket.time_created).total_seconds()/(60*60) < 24)
    tutor = current_user
    ticketID = request.form.get("ticketID")

    print("RECIEVED TICKET ID: " + str(ticketID))
    print("VALUE OF ACTION: " + str(request.form.get("action")))
    # retrieve ticket by primary key using get()
    current_ticket = m.Ticket.query.get(ticketID)

    if request.form.get("action") == "Claim":
        # edit status of ticket to Claimed, assign tutor, set time claimed
        current_ticket.tutor_id = tutor.id
        current_ticket.status = m.Status.Claimed
        current_ticket.time_claimed = _now()
        print("TIME TICKET CLAIMED: " + str(_now()))
        db.session.commit()

        print("TUTOR ID THAT CLAIMED TICKET: " + str(current_ticket.tutor_id))
    elif request.form.get("action") == "Close":
        # edit status of ticket to CLOSED and set time closed on ticket
        current_ticket.status = m.Status.Closed
        current_ticket.time_closed = _now()
        print("TIME TICKET CLOSED: " + str(_now()))
        # calculate session duration from time claimed to time closed
        duration = _calc_session_duration(current_ticket.time_claimed, current_ticket.time_closed, current_ticket.session_duration)
        print("DURATION: " + str(duration))
        # TODO: get the duration calculation accounting for business days/hours too
        current_ticket.session_duration = duration
        db.session.commit()
    elif request.form.get("action") == "ReOpen":
        # edit status of ticket back to OPEN
        current_ticket.status = m.Status.Open
        db.session.commit()

    return render_template('view_tickets.html', Status=Status, user=current_user, tutors=tutors, tickets=tickets)

@views.route('/edit-ticket', methods=["GET", "POST"])
@login_required
def edit_ticket():
    # query all tickets after possible updates and send back to view tickets page
    tickets = m.Ticket.query.all()  # .filter(_now() - Ticket.time_created).total_seconds()/(60*60) < 24)

    # get ticket id back + current ticket
    ticketID = request.form.get("ticketIDModal")
    current_ticket = m.Ticket.query.get(ticketID)

    # get the tutors to display for edit ticket modal if the user presses it
    tutors = m.User.query.filter(m.User.permission_level >= 1)

    # get info back from popup modal form
    if request.method == "POST":
        course = request.form.get("courseField")
        section = request.form.get("sectionField")
        assignment = request.form.get("assignmentNameField")
        question = request.form.get("specificQuestionField")
        problem = request.form.get("problemTypeField")
        primaryTutor = request.form.get("primaryTutorInput")
        tutorNotes = request.form.get("tutorNotes")
        wasSuccessful = request.form.get("successfulSession")
        print("Following info coming back from edit-ticket: ")

        print("current ticket ID: " + str(ticketID))
        print("course: " + str(course))
        print("section: " + str(section))
        print("assignment: " + str(assignment))
        print("question: " + str(question))
        print("problem: " + str(problem))
        print("primaryTutor: " + str(primaryTutor))
        print("tutorNotes: " + str(tutorNotes))
        print("wasSuccessful: " + str(wasSuccessful))

        # check for change in values from edit
        if course is not None:
            # new info for course came back, update it for current ticket
            current_ticket.course = course
            db.session.commit()
        if section is not None:
            # new info for section came back, update it for current ticket
            current_ticket.section = section
            db.session.commit()
        if assignment != current_ticket.assignment_name:
            # new info for assignment came back, update it for current ticket
            current_ticket.assignment_name = assignment
            db.session.commit()
        if question != current_ticket.specific_question:
            # new info for question came back, update it for current ticket
            current_ticket.specific_question = question
            db.session.commit()
        if problem is not None:
            # new info for problem came back, update it for current ticket
            current_ticket.problem_type = problem
            db.session.commit()
        if primaryTutor is not None:
            # new info for primary tutor came back, update it for current ticket

            # newTutor = m.User.query.filter(m.User.user_name == primaryTutor).first()
            print("Chaning primary tutor to: " + str(primaryTutor))
            current_ticket.tutor_id = primaryTutor
            db.session.commit()
        if tutorNotes is not None:
            # new info for tutor notes came back, update it for current ticket
            current_ticket.tutor_notes = tutorNotes
            db.session.commit()
        if wasSuccessful is not None:
            # new info for tutor notes came back, update it for current ticket
            current_ticket.successful_session = True
            db.session.commit()
        else:
            current_ticket.successful_session = False
            db.session.commit()

    return render_template('view_tickets.html', Status=Status, user=current_user, tutors=tutors, tickets=tickets)

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
    email = _strip_or_none(form.get("email"))
    name = _strip_or_none(form.get("fullname"))
    course = _strip_or_none(form.get("course"))
    section = _strip_or_none(form.get("section"))
    assignment = _strip_or_none(form.get("assignment"))
    question = _strip_or_none(form.get("question"))
    problem = _strip_or_none(form.get("problem"))

    if _str_empty(email):
        flash('Could not submit ticket, email must not be empty!', category='error')

    elif _str_empty(name):
        flash('Could not submit ticket, name must not be empty!', category='error')

    elif _str_empty(assignment):
        flash('Could not submit ticket, assignment name must not be empty!', category='error')

    elif _str_empty(question):
        flash('Could not submit ticket, question must not be empty!', category='error')

    # TODO: Check if course is a valid from a list of options
    # TODO: Check if section is valid from a list of options
    # TODO: Check if problem type is valid from a list of options

    else:
        mode_val = _strip_or_none(form.get("mode"))
        mode = None

        try:
            if mode_val:
                mode = Mode(int(mode_val))

        except ValueError:
            flash('Could not submit ticket, must select a valid mode!', category='error')

        else:
            return Ticket(email, name, course, section, assignment, question, problem, mode)

def _strip_or_none(s: str):
    return s.strip() if s is not None else None

def _str_empty(s: str):
    return s is not None and not s

def _calc_session_duration(start_time, end_time, current_session_duration):
    # print("START TIME IN: " + str(start_time))
    # print("END TIME IN: " + str(end_time))
    # print("CURRENT TIME IN: " + str(current_session_duration))

    diff = timedelta(seconds=0)
    if start_time is not None:
        diff = end_time - start_time

    # check if there is already time logged on the ticket, if so add that too
    if current_session_duration is not None:
        # python datetime and timedelta conversions
        tmp = current_session_duration
        diff = diff + timedelta(hours=tmp.hour, minutes=tmp.minute, seconds=tmp.second, microseconds=tmp.microsecond)

    # convert timedelta() object back into datetime.datetime object to set into db
    epoch = datetime(1970, 1, 1, 0, 0, 0)
    result = epoch + diff

    # chop off epoch year, month, and date. Just want HH:MM:SS (time) worked on ticket - date doesn't matter
    return result.time()

def _now():
    """
    Gets the current time in UTC.
    :return: Current time in Coordinated Universal Time (UTC)
    """
    return datetime.now()

@views.route('/admin-course', methods=["GET", "POST"])
@login_required
def add_course():

    if request.method == "POST":
        courseDepartment = _strip_or_none(request.form.get("courseDepartment"))
        courseNumber = _strip_or_none(request.form.get("courseNumber"))
        courseName = _strip_or_none(request.form.get("courseName"))
        displayOnIndex = request.form.get("displayOnIndex")
        print("COURSE DEPARTMENT: " + str(courseDepartment))
        print("COURSE NUMBER: " + str(courseNumber))
        print("COURSE NAME: " + str(courseName))
        print("DISPLAY ON INDEX: " + str(displayOnIndex))

        # set up regex
        # m = re.match("(^[A-Z]{2,4})\\s?(\\d{4})$", courseNumber)

        # set on display
        if displayOnIndex is not None:
            displayOnIndex = True
        else:
            displayOnIndex = False

        # validate the input coming in. store everything in DB the same
        if _str_empty(courseDepartment):
            flash('Could not create course, course department must not be empty!', category='error')
        elif _str_empty(courseNumber):
            flash('Could not create course, course number must not be empty!', category='error')
        elif _str_empty(courseName):
            flash('Could not create course, course name must not be empty!', category='error')
        else:

            tmpCourse = Courses.query.filter_by(number=courseNumber, course_name=courseName).first()
            if tmpCourse is None:
                newCourse = Courses(courseDepartment, courseNumber, courseName, displayOnIndex)
                db.session.add(newCourse)
                db.session.commit()
                flash('Course created successfully!', category='success')
                # TODO: return redirect for admin console home?
            else:
                flash('Course already exists in database!', category='error')
                print("COURSE ALREADY IN DB!")

    # get all courses, just for validation in html
    courses = Courses.query.all()
    return render_template('admin-course.html', courses=courses)

@views.route('/admin-semester', methods=["GET", "POST"])
@login_required
def admin_semester():

    if request.method == "POST":
        year = _strip_or_none(request.form.get("yearInput"))
        season = _strip_or_none(request.form.get("seasonInput"))
        startDate = _strip_or_none(request.form.get("startDate"))
        endDate = _strip_or_none(request.form.get("endDate"))
        print("YEAR: " + str(year))
        print("SEASON: " + str(season))
        print("START DATE: " + startDate)
        print("END DATE: " + endDate)

        # validate input coming in
        if _str_empty(year):
            flash('Could not create semester, year must not be empty!', category='error')
        elif _str_empty(season):
            flash('Could not create semester, season must not be empty!', category='error')
        elif _str_empty(startDate):
            flash('Could not create semester, start date must not be empty!', category='error')
        elif _str_empty(endDate):
            flash('Could not create semester, end date must not be empty!', category='error')
        else:
            # create semester and add it to DB, need to cast dates from string to date objects
            start = datetime.strptime(startDate, "%Y-%m-%d").date()
            end = datetime.strptime(endDate, "%Y-%m-%d").date()
            newSemester = Semesters(year, season, start, end)
            db.session.add(newSemester)
            db.session.commit()
            flash('Semester created successfully!', category='success')

    num = Semesters.query.count()
    print("NUM SEMESTERS: " + str(num))

    # get all semesters, just for validation in html
    semesters = Semesters.query.all()
    return render_template('admin-semester.html', semesters=semesters)
