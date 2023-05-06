from flask import Blueprint
from flask import request
from flask import flash
from flask import url_for
from flask import redirect
from flask import render_template

from flask_login import login_required
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from app.util import strip_or_none
from app.util import str_empty
from app.util import permission_required

from app.model import Ticket
from app.model import Mode
from app.model import Status
from app.model import User
from app.model import Course
from app.model import Semesters
from app.model import Professor
from app.model import Sections
from app.model import SectionMode
from app.model import Permission

from datetime import datetime, date, time
from datetime import timedelta

from app.extensions import db
from werkzeug.datastructures import ImmutableMultiDict

import sys
import re

views = Blueprint('views', __name__)

@views.route("/")
def index():
    return render_template('index.html')

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
        return render_template('create-ticket.html')

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
            return redirect(url_for('views.index'))

    return redirect(url_for('views.create_ticket'))

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
    tickets = Ticket.query.all()  # .filter(_now() - Ticket.time_created).total_seconds()/(60*60) < 24)

    # Get the user permission level here BEFORE attempting to load view-tickets page
    user_level = current_user.permission
    if (user_level < Permission.Tutor):
        flash('Insufficient permission level to view tickets', category='error')
        return redirect(url_for('views.index'))

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
    # get ticket id back + current ticket
    ticketID = request.form.get("ticketIDModal")
    ticket = Ticket.query.get(ticketID)

    if ticket is not None:
        _attempt_edit_ticket(ticket)

    else:
        flash('Could not edit ticket. Ticket not found in database.', category='error')

    return redirect(url_for('views.view_tickets'))

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
    email = strip_or_none(form.get("email"))
    name = strip_or_none(form.get("fullname"))
    course = strip_or_none(form.get("course"))
    section = strip_or_none(form.get("section"))
    assignment = strip_or_none(form.get("assignment"))
    question = strip_or_none(form.get("question"))
    problem = strip_or_none(form.get("problem"))

    if str_empty(email):
        flash('Could not submit ticket, email must not be empty!', category='error')

    elif str_empty(name):
        flash('Could not submit ticket, name must not be empty!', category='error')

    elif str_empty(assignment):
        flash('Could not submit ticket, assignment name must not be empty!', category='error')

    elif str_empty(question):
        flash('Could not submit ticket, question must not be empty!', category='error')

    # TODO: Check if course is a valid from a list of options
    # TODO: Check if section is valid from a list of options
    # TODO: Check if problem type is valid from a list of options

    else:
        mode_val = strip_or_none(form.get("mode"))
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

def _attempt_edit_ticket(ticket: Ticket):
    # get info back from popup modal form
    course = request.form.get("courseField")
    section = request.form.get("sectionField")
    assignment = request.form.get("assignmentNameField")
    question = request.form.get("specificQuestionField")
    problem = request.form.get("problemTypeField")
    primaryTutor = request.form.get("primaryTutorInput")
    tutorNotes = request.form.get("tutorNotes")
    wasSuccessful = request.form.get("successfulSession")

    # check for change in values from edit
    if course is not None:
        # new info for course came back, update it for current ticket
        ticket.course = course

    if section is not None:
        # new info for section came back, update it for current ticket
        ticket.section = section

    if assignment != ticket.assignment_name:
        # new info for assignment came back, update it for current ticket
        ticket.assignment_name = assignment

    if question != ticket.specific_question:
        # new info for question came back, update it for current ticket
        ticket.specific_question = question

    if problem is not None:
        # new info for problem came back, update it for current ticket
        ticket.problem_type = problem

    if primaryTutor is not None:
        # new info for primary tutor came back, update it for current ticket
        ticket.tutor_id = primaryTutor

    if tutorNotes is not None:
        # new info for tutor notes came back, update it for current ticket
        ticket.tutor_notes = tutorNotes

    if wasSuccessful is not None:
        # new info for tutor notes came back, update it for current ticket
        ticket.successful_session = True

    else:
        ticket.successful_session = False

    db.session.commit()


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
            # check if course already exists in DB, get all unison input

            tmpCourse = Course.query.filter_by(department=courseDepartment.upper(), number=courseNumber).first()
            if tmpCourse is None:
                newCourse = Course(courseDepartment.upper(), courseNumber, courseName, displayOnIndex)
                db.session.add(newCourse)
                db.session.commit()
                flash('Course created successfully!', category='success')
                # TODO: return redirect for admin console home?
            else:
                flash("Course '" + courseDepartment + " " + courseNumber + "' already exists in database!", category='error')
                print("COURSE ALREADY IN DB!")

    # get all courses
    courses = Course.query.all()
    return render_template('admin-course.html', courses=courses)

@views.route('/admin-semester', methods=["GET", "POST"])
@login_required
def add_semester():

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
        elif len(year) != 4:
            flash('Could not create semester, please enter valid year in the format YYYY!', category='error')
        else:
            # check if semester already exists in DB, impossible to have two summer 2023 semesters fo example
            tmpSemester = Semesters.query.filter_by(season=season, year=year).first()
            if tmpSemester is None:
                # create semester and add it to DB, need to cast dates from string to date objects
                start = datetime.strptime(startDate, "%Y-%m-%d").date()
                end = datetime.strptime(endDate, "%Y-%m-%d").date()
                newSemester = Semesters(year, season, start, end)
                db.session.add(newSemester)
                db.session.commit()
                flash('Semester created successfully!', category='success')
            else:
                flash("Semester '" + season + " " + year + "' already exists in database!", category='error')
                print("SEMESTER ALREADY IN DB!")

    num = Semesters.query.count()
    print("NUM SEMESTERS: " + str(num))

    # get all semesters
    semesters = Semesters.query.all()
    return render_template('admin-semester.html', semesters=semesters)

@views.route('/admin-professor', methods=["GET", "POST"])
@login_required
def add_professor():

    if request.method == "POST":
        firstName = _strip_or_none(request.form.get("firstNameInput"))
        lastName = _strip_or_none(request.form.get("lastNameInput"))
        print("FIRST NAME: " + str(firstName))
        print("LAST NAME: " + str(lastName))

        # validate input coming in
        if _str_empty(firstName):
            flash('Could not add professor, first name must not be empty!', category='error')
        elif _str_empty(lastName):
            flash('Could not add professor, last name must not be empty!', category='error')
        else:
            # check if professor already exists in DB, store all lower so checks against caps doesn't happen
            tmpProfessor = Professor.query.filter_by(first_name=firstName.lower(), last_name=lastName.lower()).first()
            if tmpProfessor is None:
                # create professor and add it to DB, store as lower
                newProfessor = Professor(firstName.lower(), lastName.lower())
                db.session.add(newProfessor)
                db.session.commit()
                flash('Professor added successfully!', category='success')
            else:
                flash("Professor '" + firstName.title() + " " + lastName.title() + "' already exists in database!", category='error')

    # get all professors
    professors = Professor.query.all()
    return render_template('admin-professor.html', professors=professors)

@views.route('/admin-sections', methods=["GET", "POST"])
@login_required
def add_section():

    if request.method == "POST":
        semester = _strip_or_none(request.form.get("semesterInput"))
        course = _strip_or_none(request.form.get("courseInput"))
        sectionNum = _strip_or_none(request.form.get("sectionNumberInput"))
        sectionMode = _strip_or_none(request.form.get("mode"))
        monInput = _strip_or_none(request.form.get("mondayTime"))
        tueInput = _strip_or_none(request.form.get("tuesdayTime"))
        wedInput = _strip_or_none(request.form.get("wednesdayTime"))
        thuInput = _strip_or_none(request.form.get("thursdayTime"))
        friInput = _strip_or_none(request.form.get("fridayTime"))
        secStartTime = _strip_or_none(request.form.get("sectionStartTime"))
        secEndTime = _strip_or_none(request.form.get("sectionEndTime"))
        professor = _strip_or_none(request.form.get("professorInput"))
        print("SEMESTER: " + semester)
        print("COURSE: " + course)
        print("SECTION NUM: " + sectionNum)
        print("SECTION MODE: " + str(sectionMode))
        print("MONDAY: " + str(monInput))
        print("TUESDAY: " + str(tueInput))
        print("WEDNESDAY: " + str(wedInput))
        print("THURSDAY: " + str(thuInput))
        print("FRIDAY: " + str(friInput))
        print("SEC START: " + secStartTime)
        print("SEC END: " + secEndTime)
        print("PROFESSOR: " + professor)

        # validate input coming in
        if monInput is None and tueInput is None and wedInput is None and thuInput is None and friInput is None and sectionMode != "TotallyOnline":
            flash('Could not create section, must provide atleast one day of the week for section if mode is ' + str(sectionMode) + '!', category='error')
        elif (sectionMode == "Remote" or sectionMode == "InPerson") and (secStartTime == "" or secEndTime == ""):
            flash('Could not create section, must provide both start and end time for section if mode is ' + str(sectionMode) + '!', category='error')
        else:
            # check if section already exists in DB
            tmpSection = Sections.query.filter_by(section_number=sectionNum, course_id=course).first()
            if tmpSection is None:
                # create section and add it to DB
                # need to assemble days of week string to set in DB
                daysOfWeek = ""
                if sectionMode != "TotallyOnline":
                    if monInput is not None:
                        daysOfWeek = daysOfWeek + "Mon"
                    if tueInput is not None:
                        daysOfWeek = daysOfWeek + "Tue"
                    if wedInput is not None:
                        daysOfWeek = daysOfWeek + "Wed"
                    if thuInput is not None:
                        daysOfWeek = daysOfWeek + "Thu"
                    if friInput is not None:
                        daysOfWeek = daysOfWeek + "Fri"

                # need to assemble python time object to set in db
                try:
                    if secStartTime is not None:
                        secStartTime = datetime.strptime(secStartTime, '%H:%M').time()
                        print("IT IS NONE: " + str(secStartTime))
                    if secEndTime is not None:
                        secEndTime = datetime.strptime(secEndTime, '%H:%M').time()
                        print(secStartTime)
                except ValueError:
                    # start and end dates are empty strings because mode = totally online. set time to 00:00
                    print("Start and end dates are empy strings because it is totaly online course.")
                    print("START TIME: " + str(secStartTime))
                    print("END TIME: " + str(secEndTime))
                    secStartTime = datetime.strptime("00:00", '%H:%M').time()
                    secEndTime = datetime.strptime("00:00", '%H:%M').time()
                    print("START TIME: " + str(secStartTime))
                    print("END TIME: " + str(secEndTime))

                newSection = Sections(sectionNum, daysOfWeek, secStartTime, secEndTime, sectionMode, course, semester, professor)
                db.session.add(newSection)
                db.session.commit()
                flash('Section added successfully!', category='success')
            else:
                flash("Section " + sectionNum + " for the course '" + course.course_name + "' already exists in DB!", category='error')

    # get all sections
    sections = Sections.query.all()
    semesters = Semesters.query.all()
    courses = Course.query.all()
    professors = Professor.query.all()
    return render_template('admin-sections.html', sections=sections, semesters=semesters, courses=courses, professors=professors, SectionMode=SectionMode)
