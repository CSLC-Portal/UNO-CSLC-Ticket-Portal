from flask import Blueprint
from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .. import model as m
from datetime import datetime, timedelta, time, date
from time import strftime
from app.extensions import db

views = Blueprint('views', __name__)

def now():
    """
    Gets the current time in UTC.
    :return: Current time in Coordinated Universal Time (UTC)
    """
    return datetime.now()

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
    mode = request.form['modeOfTicket']
    print(f"Following ticket information has been created:\n{lastName}\n{firstName}\n{email}\n{course}\n{section}\n{assignment}\n{question}\n{problem}\n{mode}")

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
            mode)

        # insert into 'Tickets' table
        db.session.add(ticket)
        db.session.commit()

    return render_template('open-tickets.html', email=email, firstName=firstName, lastName=lastName, course=course,
                           section=section, assignmentName=assignment, specificQuestion=question, problemType=problem, mode=mode)

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
    return render_template('view_tickets.html', tickets=tickets, m=m, user=current_user)

def calc_session_duration(start_time, end_time, current_session_duration):
    print("START TIME IN: " + str(start_time))
    print("END TIME IN: " + str(end_time))
    print("CURRENT TIME IN: " + str(current_session_duration))

    diff = end_time - start_time

    # check if there is already time logged on the ticket, if so add that too
    if current_session_duration is not None:
        # python datetime and timedelta conversions
        tmp = current_session_duration
        diff = diff + timedelta(hours=tmp.hour, minutes=tmp.minute, seconds=tmp.second, microseconds=tmp.microsecond)

    # convert timedelta() object back into datetime.datetime object to set into db
    epoch = datetime(1970, 1, 1, 0, 0, 0)
    result = epoch + diff

    # chop off epoch year, month, and date. Just want HH:MM:SS (time) worked on ticket - date doesn't matter
    return result.time()

@views.route('/update-ticket', methods=["GET", "POST"])
@login_required
def update_ticket():
    """
    This function handles the HTTP request when a tutor hits the claim, close, or reopen buttons on tickets
    :return: Render template to the original view-ticket.html page.
    """
    tickets = m.Ticket.query.all()
    tutor = current_user
    ticketID = request.form.get("ticketID")

    print("RECIEVED TICKET ID: " + str(ticketID))
    print("VALUE OF ACTION: " + str(request.form.get("action")))
    # retrieve ticket by primary key using get()
    current_ticket = m.Ticket.query.get(ticketID)

    if request.form.get("action") == "Claim":
        # edit status of ticket to Claimed, assign tutor, set time claimed
        current_ticket.tutor_id = tutor.id
        current_ticket.status = m.Status.Claimed
        current_ticket.time_claimed = now()
        print("TIME TICKET CLAIMED: " + str(now()))
        db.session.commit()

        print("TUTOR ID THAT CLAIMED TICKET: " + str(current_ticket.tutor_id))
    elif request.form.get("action") == "Close":
        # edit status of ticket to CLOSED and set time closed on ticket
        current_ticket.status = m.Status.Closed
        current_ticket.time_closed = now()
        print("TIME TICKET CLOSED: " + str(now()))
        # calculate session duration from time claimed to time closed
        duration = calc_session_duration(current_ticket.time_claimed, current_ticket.time_closed, current_ticket.session_duration)
        print("DURATION: " + str(duration))
        # TODO: get the duration calculation accounting for business days/hours too
        current_ticket.session_duration = duration
        db.session.commit()
    elif request.form.get("action") == "ReOpen":
        # edit status of ticket back to OPEN
        current_ticket.status = m.Status.Open
        db.session.commit()

    return render_template('view_tickets.html', tickets=tickets, m=m, user=current_user)
