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
    if request.method == 'POST':
        email = request.form.get("email")
        name = request.form.get("fullname")
        course = request.form.get("course")
        section = request.form.get("section")
        assignment = request.form.get("assignment")
        question = request.form.get("question")
        problem = request.form.get("problem")

        try:
            ticket = Ticket(email, name, course, section, assignment, question, problem, Mode.Online)
            db.session.add(ticket)
            db.session.commit()

        except IntegrityError:
            flash('Could not submit ticket, invalid data', category='error')

        except Exception as e:
            flash('Could not submit ticket, unknown reason', category='error')
            print(f'Failed to create ticket: {e}', file=sys.stderr)

        return redirect(url_for('auth.index'))

    else:
        return render_template('create-ticket.html')

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
