from flask import Blueprint
from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .. import model as m
from datetime import datetime, timedelta
from app.extensions import db

views = Blueprint('views', __name__)

def now():
    # gets the current time, function for consistency
    return datetime.now()

@views.route('/create-ticket')
@login_required
def create_ticket():
    return render_template('create-ticket.html')

@views.route('/open-tickets', methods=["POST"])
@login_required
def open_tickets():
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
    This funciton handels the HTTP route /view-tickets, which is a page for tutors to view all tickets
    Tickets from all statuses will be returned including recently closed ones.
    Admin will be able to choose how long closed tickets should remain in the view-tickets view.
    """
    # get all tickets
    tickets = m.Ticket.query.all()
    return render_template('view_tickets.html', tickets=tickets, m=m, user=current_user)

def calc_session_duration(start_time, end_time, current_session_duration):
    # validate times are set
    if not start_time or not end_time or not isinstance(start_time, datetime) or not isinstance(end_time, datetime):
        print("START TIME IN: " + str(start_time))
        print("END TIME IN: " + str(end_time))
        print("CURRENT TIME IN: " + str(current_session_duration))
        #raise ValueError("Invalid start_time or end_time")
    # start of the day is currently 9:00 AM
    start_of_day = datetime.strptime(start_time.strftime('%m-%d-%Y') + " 09:00:00", '%m-%d-%Y %H:%M:%S')
    # end of the day is currently 5:00 PM
    end_of_day = datetime.strptime(end_time.strftime('%m-%d-%Y') + " 17:00:00", '%m-%d-%Y %H:%M:%S')
    time_worked = timedelta()

    if start_time < start_of_day:
        start_time = start_of_day

    if end_time > end_of_day:
        end_time = end_of_day

    while start_time < end_time:
        if start_time.weekday() < 5:
            if start_time.hour >= 9 and start_time.hour < 17:
                time_worked += timedelta(minutes=1)

        start_time += timedelta(minutes=1)

    # add current work done on ticket if there is any
    if current_session_duration != None:
        return time_worked + current_session_duration
    else:
        return time_worked

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
        #current_ticket.session_duration = duration
        print("TICKET DURATION: " + str(duration))
        db.session.commit()
    elif request.form.get("action") == "ReOpen":
        # edit status of ticket back to OPEN
        current_ticket.status = m.Status.Open
        db.session.commit()

    return render_template('view_tickets.html', tickets=tickets, m=m, user=current_user)





