from flask import Blueprint, Response, send_from_directory
from flask import request
from flask import flash
from flask import url_for
from flask import redirect
from flask import render_template
import csv
import os
import io

from app.model import ProblemType
from app.model import Ticket
from app.extensions import db
import datetime
from flask_login import current_user

from app.model import User
from app.model import Course
from app.model import Permission
from sqlalchemy.exc import IntegrityError

from app.util import str_empty
from app.util import strip_or_none
from app.util import permission_required

import sys

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/')
@permission_required(Permission.Admin)
def console():
    return render_template('admin-console.html')

def _strip_or_none(s: str):
    return s.strip() if s is not None else None

def _str_empty(s: str):
    return s is not None and not s

@admin.route('/problems', methods=["GET", "POST"])
def add_problem_type():
    if request.method == "POST":
        problemType = _strip_or_none(request.form.get("problemType"))
        print("PROBLEM TYPE: " + str(problemType))

        # validate the input coming in. store everything in DB the same
        if _str_empty(problemType):
            flash('Could not create problem Type, problem type must not be empty!', category='error')
        else:
            tmpCourse = ProblemType.query.filter_by(problem_type=problemType).first()
            if tmpCourse is None:
                newCourse = ProblemType(problemType)
                db.session.add(newCourse)
                db.session.commit()
                flash('Problem Type created successfully!', category='success')
                # TODO: return redirect for admin console home?
            else:
                flash('Problem Type already exists in database!', category='error')
                print("Problem Type ALREADY IN DB!")

    problemTypes = ProblemType.query.all()
    return render_template('admin-problem-types.html', problemTypes=problemTypes)

@admin.route('/download', methods=["GET", "POST"])
def download_report():

    createDate = request.form.get("creationDate")
    closeDate = request.form.get("closedDate")

    courseName = _strip_or_none(request.form.get("course"))

    if courseName:
        sub = Ticket.query.filter(Ticket.time_created >= createDate, Ticket.time_closed <= closeDate, Ticket.course == courseName).all()
    else:
        sub = Ticket.query.filter(Ticket.time_created >= createDate, Ticket.time_closed <= closeDate).all()

    global format
    format = [
        ['Student Email', 'Student Name', 'Course', 'Section', 'Assignment Name', 'Specific Question', 'Problem Type', 'Time Created', 'Time Claimed',
         'Status', 'Time Closed', 'Session Duration', 'Mode', 'Tutor Notes', 'Tutor Id', 'Successful Session']
    ]
    ticketList = list(sub)
    lengthTickets = len(ticketList)

    for i in range(len(ticketList)):
        format.append([ticketList[i].student_email, ticketList[i].student_name, ticketList[i].course, ticketList[i].section, ticketList[i].assignment_name, 
                       ticketList[i].specific_question, ticketList[i].problem_type, ticketList[i].time_created, ticketList[i].time_claimed,
                       ticketList[i].status, ticketList[i].time_closed, ticketList[i].session_duration, ticketList[i].mode, ticketList[i].tutor_notes, 
                       ticketList[i].tutor_id, ticketList[i].successful_session])

    if request.method == "POST":
        start = request.form.get("creationDate")
        end = _strip_or_none(request.form.get("closedDate"))

        print(start)
        print(end)

    return render_template('download-report.html', sub=sub, lengthTickets=lengthTickets)


@admin.route('/download_csv', methods=["GET", "POST"])
def download_csv():
    file = io.StringIO()
    writer = csv.writer(file)
    for line in format:
        writer.writerow(line)

    return Response(file.getvalue(), content_type='text/csv', headers={'Content-Disposition': 'attachment;filename=cslc_report.csv'})


def fix_dde(cell):
    '''
    Handles a vulnerability with embedded formulae in csv files
    '''
    if cell is not None:
        cell = str(cell)
        if cell.startswith(('=', '+', '-', '@')):
            cell = "' " + cell
        cell = cell.rstrip()
    return cell
  
@admin.route('/tutors')
@permission_required(Permission.Admin)
def view_tutors():

    # NOTE: Cannot use inequality operators < > <= >= on enum from database as only
    #       the enum name is actually persisted.
    #
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

        user: User = User.query.filter_by(email=email).one_or_none()

        if str_empty(email):
            flash('Email must not be empty!', category='error')

        elif permission and current_user.permission <= permission:
            flash('Cannot add user of higher or equal permission level as yourself!', category='error')

        elif user and user.permission > Permission.Student:
            flash('User already exists in the role hierarchy!', category='error')

        elif user and user.permission == Permission.Student:
            user.tutor_is_active = True
            user.permission = permission
            db.session.commit()
            flash('New user successfully added!', category='success')

        else:
            create_pseudo_super_user(email, permission)
            flash('New user successfully added!', category='success')

    except ValueError:
        flash('Could not add user, must select a valid mode!', category='error')

    except IntegrityError:
        db.session.rollback()
        flash('Could not add user, invalid data!', category='error')

    except Exception as e:
        flash('Could not add user, unknown reason!', category='error')
        print(f'Could not add user, {e}', file=sys.stderr)

    return redirect(url_for('admin.view_tutors'))

@admin.route('/tutors/remove', methods=['POST'])
@permission_required(Permission.Admin)
def remove_tutor():
    user_id = strip_or_none(request.form.get("userID"))

    try:
        user: User = User.query.get(user_id)

        if not user:
            flash('Could not remove user, user does not exist!', category='error')

        elif user == current_user:
            flash('You cannot remove yourself from the role hierarchy!', category='error')

        elif current_user.permission <= user.permission:
            flash('Cannot remove user of higher or equal permission level as yourself!', category='error')

        else:
            _attempt_delete_super_user(user)
            flash('User successfully removed!', category='success')

    except IntegrityError:
        db.session.rollback()
        flash('Could not remove user, invalid data!', category='error')

    except Exception as e:
        flash('Could not remove user, unknown reason', category='error')
        print(f'Failed to remove user: {e}', file=sys.stderr)

    return redirect(url_for('admin.view_tutors'))

@admin.route('/tutors/edit', methods=['POST'])
@permission_required(Permission.Admin)
def edit_tutor():
    user_id = strip_or_none(request.form.get("userID"))
    permission_val = strip_or_none(request.form.get("permission"))
    active = request.form.get("active") is not None

    try:
        user: User = User.query.get(user_id)

        new_permission = None
        if permission_val:
            new_permission = Permission(int(permission_val))

        if not user:
            flash('Could not update user, user does not exist!', category='error')

        elif user == current_user:
            flash('You cannot update yourself!', category='error')

        elif current_user.permission <= user.permission:
            flash('Cannot update user of higher or equal permission level as yourself!', category='error')

        elif new_permission and current_user.permission <= new_permission:
            flash('Cannot promote user to higher or equal permission level as yourself!', category='error')

        else:
            _attempt_edit_user(user, active, new_permission)
            flash('User successfully updated!', category='success')

    except ValueError:
        flash('Could not update user, input values invalid!', category='error')

    except IntegrityError:
        flash('Could not update user, invalid data!', category='error')

    except Exception as e:
        flash('Could not update user, unknown reason!', category='error')
        print(f'Could not update user, {e}', file=sys.stderr)

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

    # set up regex
    # m = re.match("(^[A-Z]{2,4})\\s?(\\d{4})$", courseNumber)

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

def create_pseudo_super_user(email: str, permission: Permission):
    """
    If the user doesn't exist, creates and inserts an 'incomplete' user into the database given an email and permission level.
    When the user signs in using their email, the remaining info will be automatically updated in the database.

    If the user exist, the the permission level is updated for the user.
    """

    pseudo_user = User(None, permission, email, None, True, False)
    db.session.add(pseudo_user)
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

def _attempt_edit_user(user: User, active, permission=None):
    try:
        if permission:
            user.permission = permission

        user.tutor_is_active = active
        db.session.commit()

    except IntegrityError as e:
        db.session.rollback()
        raise e
