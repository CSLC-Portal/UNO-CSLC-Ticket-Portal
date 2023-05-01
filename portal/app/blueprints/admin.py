from flask import Blueprint
from flask import flash
from flask import url_for
from flask import redirect
from flask import request
from flask import render_template

from app.model import User
from app.model import Permission

from app.extensions import db
from sqlalchemy.exc import IntegrityError

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
    return render_template('admin-tutors.html', tutors=User.get_tutors())

@admin.route('/tutors/add', methods=['POST'])
@permission_required(Permission.Admin)
def add_tutor():

    email = strip_or_none(request.form.get("email"))
    permission_val = strip_or_none(request.form.get("permission"))
    permission = None

    try:
        if permission_val:
            permission = Permission(int(permission_val))

        create_pseudo_user(email, permission)

    except ValueError:
        flash('Could not submit ticket, must select a valid mode!', category='error')

    except IntegrityError:
        db.session.rollback()
        flash('Could not create pseudo user, invalid data', category='error')

    except Exception as e:
        flash('Could not create psuedo user, unknown reason', category='error')
        print(f'Failed to create pseudo user: {e}', file=sys.stderr)

    else:
        flash('New user successfully added!', category='success')

    return redirect(url_for('admin.view_tutors'))

def create_pseudo_user(email, permission):
    """
    Creates and inserts into the database an 'incomplete' user given an email and permission level.
    When the user signs in using their email, the remaining info will be automatically updated
    in the database.
    """
    pseudo_user = User(None, permission, email, None, False, False)
    db.session.add(pseudo_user)
    db.session.commit()
