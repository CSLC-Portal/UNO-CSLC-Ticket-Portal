from flask import Blueprint
from flask import request
from flask import flash
from flask import url_for
from flask import redirect
from flask import render_template

from flask_login import login_required
from sqlalchemy.exc import IntegrityError

from ..model import Ticket
from ..model import Mode
from ..model import Status

from app.extensions import db
from werkzeug.datastructures import ImmutableMultiDict

import sys

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
    tickets = Ticket.query.all()

    return render_template('view_tickets.html', tickets=tickets, Status=Status)

# TODO: Look into using flask-wtf for form handling and validation

def _attempt_create_ticket(form: ImmutableMultiDict):
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
        return Ticket(email, name, course, section, assignment, question, problem, Mode.Online)

def _strip_or_none(s: str):
    return s.strip() if s is not None else None

def _str_empty(s: str):
    return s is not None and not s
