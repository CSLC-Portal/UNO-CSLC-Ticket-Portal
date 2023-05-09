from flask import Blueprint
from flask import flash
from flask import url_for
from flask import redirect
from flask import request
from flask import render_template

from flask_login import current_user

from app.model import User
from app.model import Course
from app.model import Permission
from app.model import Section
from app.model import Professor
from app.model import Semester
from app.model import SectionMode

from datetime import datetime

from app.extensions import db
from sqlalchemy.exc import IntegrityError

from app.util import str_empty
from app.util import strip_or_none
from app.util import permission_required
from app.util import build_days_of_week_string

import sys

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/')
@permission_required(Permission.Admin)
def console():
    return render_template('admin-console.html')

@admin.route('/tutors')
@permission_required(Permission.Admin)
def view_tutors():
    return render_template('admin-tutors.html')

@admin.route('/tutors/add', methods=['POST'])
@permission_required(Permission.Admin)
def add_tutor():

    email = strip_or_none(request.form.get("email"))
    permission_val = strip_or_none(request.form.get("permission"))
    permission = None

    try:
        if permission_val:
            permission = Permission(int(permission_val))

        # TODO: Should display error message if user is already set at the permission level
        attempt_create_super_user(email, permission)

    except ValueError:
        flash('Could not add user, must select a valid mode!', category='error')

    except IntegrityError:
        db.session.rollback()
        flash('Could not add user, invalid data', category='error')

    except Exception as e:
        flash('Could not add user, unknown reason', category='error')
        print(f'Failed to create pseudo user: {e}', file=sys.stderr)

    else:
        flash('New user successfully added!', category='success')

    return redirect(url_for('admin.view_tutors'))

@admin.route('/tutors/remove', methods=['POST'])
@permission_required(Permission.Admin)
def remove_tutor():
    user_id = strip_or_none(request.form.get("userID"))

    try:
        user: User = User.query.get(user_id)

        if user and user != current_user:
            # TODO: Should display error message if user has permission level of Student
            _attempt_delete_super_user(user)
            flash('User successfully removed!', category='success')

        elif user == current_user:
            flash('You cannot remove yourself from the role hierarchy!', category='error')

        else:
            flash('Could not remove user, user does not exist!', category='error')

    except IntegrityError:
        db.session.rollback()
        flash('Could not remove user, invalid data!', category='error')

    except Exception as e:
        flash('Could not remove user, unknown reason', category='error')
        print(f'Failed to remove user: {e}', file=sys.stderr)

    return redirect(url_for('admin.view_tutors'))

@admin.route('/courses')
@permission_required(Permission.Admin)
def view_courses():
    # get all courses, just for validation in html
    courses = Course.query.all()
    return render_template('admin-course.html', courses=courses)

@admin.route('/courses/add', methods=["POST"])
@permission_required(Permission.Admin)
def add_course():

    courseDepartment = strip_or_none(request.form.get("courseDepartment"))
    courseNumber = strip_or_none(request.form.get("courseNumber"))
    courseName = strip_or_none(request.form.get("courseName"))
    displayOnIndex = request.form.get("displayOnIndex")
    print("COURSE DEPARTMENT: " + str(courseDepartment))
    print("COURSE NUMBER: " + str(courseNumber))
    print("COURSE NAME: " + str(courseName))
    print("DISPLAY ON INDEX: " + str(displayOnIndex))

    # set on display
    if displayOnIndex is not None:
        displayOnIndex = True
    else:
        displayOnIndex = False

    # validate the input coming in. store everything in DB the same
    if str_empty(courseDepartment):
        flash('Could not create course, course department must not be empty!', category='error')
    elif str_empty(courseNumber):
        flash('Could not create course, course number must not be empty!', category='error')
    elif str_empty(courseName):
        flash('Could not create course, course name must not be empty!', category='error')
    else:

        tmpCourse = Course.query.filter_by(number=courseNumber, course_name=courseName).first()
        if tmpCourse is None:
            newCourse = Course(courseDepartment, courseNumber, courseName, displayOnIndex)
            db.session.add(newCourse)
            db.session.commit()
            flash('Course created successfully!', category='success')
            # TODO: return redirect for admin console home?
        else:
            flash('Course already exists in database!', category='error')
            print("COURSE ALREADY IN DB!")

    return redirect(url_for('admin.view_courses'))

@admin.route('/courses/remove', methods=['POST'])
@permission_required(Permission.Admin)
def remove_course():

    course_id = strip_or_none(request.form.get("courseID"))

    try:
        course: Course = Course.query.get(course_id)

        if course:
            db.session.delete(course)
            print("DELETED: " + str(course))  # this will automatically delete any sections associated with this course
            print("Sections associated with course: " + str(len(course.sections)))
            flash('Course successfully removed!', category='success')
        else:
            flash('Could not remove course, course does not exist!', category='error')

    except IntegrityError:
        db.session.rollback()
        flash('Could not remove course, invalid data!', category='error')

    except Exception as e:
        flash('Could not remove course, unknown reason', category='error')
        print(f'Failed to remove course: {e}', file=sys.stderr)

    return redirect(url_for('admin.view_courses'))

@admin.route('/semesters')
@permission_required(Permission.Admin)
def view_semesters():
    # get all courses, just for validation in html
    semesters = Semester.query.all()
    return render_template('admin-semester.html', semesters=semesters)

@admin.route('/semesters/add', methods=["POST"])
@permission_required(Permission.Admin)
def add_semester():

    year = strip_or_none(request.form.get("yearInput"))
    season = strip_or_none(request.form.get("seasonInput"))
    startDate = strip_or_none(request.form.get("startDate"))
    endDate = strip_or_none(request.form.get("endDate"))
    print("YEAR: " + str(year))
    print("SEASON: " + str(season))
    print("START DATE: " + startDate)
    print("END DATE: " + endDate)

    # validate input coming in
    if str_empty(year):
        flash('Could not create semester, year must not be empty!', category='error')
    elif str_empty(season):
        flash('Could not create semester, season must not be empty!', category='error')
    elif str_empty(startDate):
        flash('Could not create semester, start date must not be empty!', category='error')
    elif str_empty(endDate):
        flash('Could not create semester, end date must not be empty!', category='error')
    elif len(year) != 4:
        flash('Could not create semester, please enter valid year in the format YYYY!', category='error')
    else:
        # check if semester already exists in DB, impossible to have two summer 2023 semesters fo example
        tmpSemester = Semester.query.filter_by(season=season, year=year).first()
        if tmpSemester is None:
            # create semester and add it to DB, need to cast dates from string to date objects
            start = datetime.strptime(startDate, "%Y-%m-%d").date()
            end = datetime.strptime(endDate, "%Y-%m-%d").date()
            newSemester = Semester(year, season, start, end)
            db.session.add(newSemester)
            db.session.commit()
            flash('Semester created successfully!', category='success')
        else:
            flash("Semester '" + season + " " + year + "' already exists in database!", category='error')
            print("SEMESTER ALREADY IN DB!")

    num = Semester.query.count()
    print("NUM SEMESTERS: " + str(num))

    return redirect(url_for('admin.view_semesters'))

@admin.route('/semesters/remove', methods=['POST'])
@permission_required(Permission.Admin)
def remove_semester():

    semester_id = strip_or_none(request.form.get("semesterID"))

    try:
        semester: Semester = Semester.query.get(semester_id)

        if semester:
            db.session.delete(semester)
            print("DELETED SEMESTER: " + str(semester))
            flash('Semester successfully removed!', category='success')
        else:
            flash('Could not remove semester, course does not exist!', category='error')

    except IntegrityError:
        db.session.rollback()
        flash('Could not remove semester, invalid data!', category='error')

    except Exception as e:
        flash('Could not remove semester, unknown reason', category='error')
        print(f'Failed to remove semester: {e}', file=sys.stderr)

    return redirect(url_for('admin.view_semesters'))

@admin.route('/professors')
@permission_required(Permission.Admin)
def view_professors():
    # get all courses, just for validation in html
    professors = Professor.query.all()
    return render_template('admin-professor.html', professors=professors)

@admin.route('/professors/add', methods=["POST"])
@permission_required(Permission.Admin)
def add_professor():

    firstName = strip_or_none(request.form.get("firstNameInput"))
    lastName = strip_or_none(request.form.get("lastNameInput"))
    print("FIRST NAME: " + str(firstName))
    print("LAST NAME: " + str(lastName))

    # validate input coming in
    if str_empty(firstName):
        flash('Could not add professor, first name must not be empty!', category='error')
    elif str_empty(lastName):
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

    return redirect(url_for('admin.view_professors'))

@admin.route('/sections')
@permission_required(Permission.Admin)
def view_sections():
    # get all courses, just for validation in html
    sections = Section.query.all()
    semesters = Semester.query.all()
    courses = Course.query.all()
    professors = Professor.query.all()
    return render_template('admin-sections.html', sections=sections, semesters=semesters, courses=courses, professors=professors)

@admin.route('/sections/add', methods=["POST"])
@permission_required(Permission.Admin)
def add_section():

    semester = strip_or_none(request.form.get("semesterInput"))
    course = strip_or_none(request.form.get("courseInput"))
    sectionNum = strip_or_none(request.form.get("sectionNumberInput"))
    sectionMode = strip_or_none(request.form.get("mode"))
    monInput = strip_or_none(request.form.get("mondayTime"))
    tueInput = strip_or_none(request.form.get("tuesdayTime"))
    wedInput = strip_or_none(request.form.get("wednesdayTime"))
    thuInput = strip_or_none(request.form.get("thursdayTime"))
    friInput = strip_or_none(request.form.get("fridayTime"))
    secStartTime = strip_or_none(request.form.get("sectionStartTime"))
    secEndTime = strip_or_none(request.form.get("sectionEndTime"))
    professor = strip_or_none(request.form.get("professorInput"))
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
        tmpSection = Section.query.filter_by(section_number=sectionNum, course_id=course).first()
        if tmpSection is None:
            # create section and add it to DB
            # need to assemble days of week string to set in DB
            daysOfWeek = ""
            if sectionMode != "TotallyOnline":
                daysOfWeek = build_days_of_week_string(monInput, tueInput, wedInput, thuInput, friInput)

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

            newSection = Section(sectionNum, daysOfWeek, secStartTime, secEndTime, sectionMode, course, semester, professor)
            db.session.add(newSection)
            db.session.commit()
            flash('Section added successfully!', category='success')
        else:
            flash("Section " + sectionNum + " for the course '" + course.course_name + "' already exists in DB!", category='error')

    return redirect(url_for('admin.view_sections'))

def attempt_create_super_user(email: str, permission: Permission):
    """
    If the user doesn't exist, creates and inserts an 'incomplete' user into the database given an email and permission level.
    When the user signs in using their email, the remaining info will be automatically updated in the database.

    If the user exist, the the permission level is updated for the user.
    """

    if str_empty(email):
        # NOTE: Don't want to create custom exception class right now
        #       Most of this should be handled by flask-wtf anyways in the future
        #
        raise Exception('Email must not be empty')

    user: User = User.query.filter_by(email=email).one_or_none()

    if user is None:
        pseudo_user = User(None, permission, email, None, True, False)
        db.session.add(pseudo_user)

    else:
        user.tutor_is_active = True
        user.permission = permission

    db.session.commit()

def _attempt_delete_super_user(user: User):
    """
    If the user is complete then their permissions will be set to the lowest level.
    However, they will remain in the database and past information will be retained.

    If the user is not complete then they will be removed from the database.
    """

    # The user was never completed, we can delete this record
    if not user.is_complete():
        # print(f'{user} is not a completed user, removing from database...')
        db.session.delete(user)

    else:
        # print(f'{user}\'s permissions changing to {Permission.Student}...')
        user.tutor_is_active = False
        user.permission = Permission.Student

    db.session.commit()
