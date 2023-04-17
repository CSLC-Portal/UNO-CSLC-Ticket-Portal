from flask import Blueprint
from flask import request
from flask import url_for
from flask import redirect
from flask import render_template

from flask_login import login_required

from ..model import Ticket
from ..model import Mode
from ..model import Status

from app.extensions import db

views = Blueprint('views', __name__)

@views.route('/create-ticket', methods=['POST', 'GET'])
@login_required
def create_ticket():
    """
    Serves the HTTP route /create-ticket. Utilizes the flask funciton 'render_template' to render
    the passed in create-ticket.html template which is the form that students use to create/submit tickets.

    Student login is required to access this page.
    """
    if request.method == 'POST':
        email = request.form.get("emailAdressField")
        name = request.form.get("firstNameField")
        course = request.form.get("courseField")
        section = request.form.get("sectionField")
        assignment = request.form.get("assignmentNameField")
        question = request.form.get("specificQuestionField")
        problem = request.form.get("problemTypeField")

        # insert into 'Tickets' table
        ticket = Ticket(email, name, course, section, assignment, question, problem, Mode.Online)
        db.session.add(ticket)
        db.session.commit()

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
