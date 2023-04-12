from flask import Blueprint
from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .. import model as m
import datetime
from app.extensions import db

views = Blueprint('views', __name__)

def now():
    """
    Gets the current time in UTC.
    :return: Current time in Coordinated Universal Time (UTC)
    """
    UTC = datetime.timezone.utc
    now = datetime.datetime.now(UTC)
    return now

@views.route('/create-ticket')
@login_required
def create_ticket():
    """
    Serves the HTTP route /create-ticket. Utilizes the flask funciton 'render_template' to render
    the passed in create-ticket.html template which is the form that students use to create/submit tickets.

    Student login is required to access this page.
    """
    return render_template('create-ticket.html')

@views.route('/open-tickets', methods=["POST"])
@login_required
def open_tickets():
    """
    Serves the HTTP route /open-tickets. This is a debugging page for the developers to verify that the
    ticket that they just created is being successfuly inserted into the database with the proper information
    being sent back to the backend processing service.

    Utilizes the flask funciton 'render_template' to render the passed in open-tickets.html template which is
    used to display form data that is sent from the create-ticket.html form.

    Student login is required to access this page.
    """
    email = request.form.get("emailAdressField")
    firstName = request.form.get("firstNameField")
    lastName = request.form.get("lastNameField")
    course = request.form.get("courseField")
    section = request.form.get("sectionField")
    assignment = request.form.get("assignmentNameField")
    question = request.form.get("specificQuestionField")
    problem = request.form.get("problemTypeField")
    print(f"Following ticket information has been created:\n{lastName}\n{firstName}\n{email}\n{course}\n{section}\n{assignment}\n{question}\n{problem}")

    # create ticket with info sent back
    if request.method == "POST":
        ticket = m.Ticket(
            email,
            firstName,
            course,
            section,
            assignment,
            question,
            problem,
            now(),
            m.Mode.Online)

        # insert into 'Tickets' table
        db.session.add(ticket)
        db.session.commit()

    return render_template('open-tickets.html', email=email, firstName=firstName, lastName=lastName, course=course,
                           section=section, assignmentName=assignment, specificQuestion=question, problemType=problem)

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
    # get all tickets
    tickets = m.Ticket.query.all()
    print("TICKETS+++++++++++++ " + str(tickets))

    return render_template('view_tickets.html', tickets=tickets, m=m)
