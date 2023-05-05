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

from app.extensions import db
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
