from flask import Blueprint
from flask import flash
from flask import url_for
from flask import redirect
from flask import request
from flask import render_template

from flask_login import current_user

from app.model import User
from app.model import Course
from app.model import Message
from app.model import Permission

from app.extensions import db
from sqlalchemy.exc import IntegrityError

from app.util import str_empty
from app.util import strip_or_none
from app.util import permission_required

import sys
import datetime

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/')
@permission_required(Permission.Admin)
def console():
    return render_template('admin-console.html')

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

@admin.route('/messages')
@permission_required(Permission.Admin)
def view_messages():
    # get all courses, just for validation in html
    messages = Message.query.all()
    return render_template('admin-messages.html', messages=messages)

@admin.route('/messages/add', methods=["POST"])
@permission_required(Permission.Admin)
def add_message():

    message = strip_or_none(request.form.get("message"))
    startDate = datetime.datetime.strptime(request.form.get("startDate"), "%Y-%m-%d")
    endDate = datetime.datetime.strptime(request.form.get("endDate"), "%Y-%m-%d")
    print("MESSAGE: " + str(message))
    print("START DATE: " + str(startDate))
    print("END DATE: " + str(endDate))

    newMessage = Message(message, startDate, endDate)
    db.session.add(newMessage)
    db.session.commit()
    flash('Message added successfully!', category='success')

    return redirect(url_for('admin.view_messages'))

@admin.route('/messages/remove', methods=["POST"])
@permission_required(Permission.Admin)
def remove_message():
    message_id = strip_or_none(request.form.get("messageID"))
    try:
        message: Message = Message.query.get(message_id)

        if not message:
            flash('Could not remove message, message does not exist!', category='error')

        else:
            db.session.delete(message)
            db.session.commit()
            flash('message successfully removed!', category='success')

    except IntegrityError:
        db.session.rollback()
        flash('Could not remove message, invalid data!', category='error')

    except Exception as e:
        flash('Could not remove message, unknown reason', category='error')
        print(f'Failed to remove message: {e}', file=sys.stderr)

    return redirect(url_for('admin.view_messages'))

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
