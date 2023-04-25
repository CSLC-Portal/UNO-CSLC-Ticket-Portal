from flask import Blueprint
from flask import request
from flask import flash
from flask import url_for
from flask import redirect
from flask import render_template

from flask_login import login_required
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from ..model import Ticket
from ..model import Mode
from ..model import Status
from ..model import User

from datetime import datetime
from datetime import timedelta

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
        - mode: Whether the student is online or in-person

    Then redirects back to the home page.

    Utilizes the flask funciton 'render_template' to render
    the passed in create-ticket.html template which is the form that students use to create/submit tickets.

    Student login is required to access this page.
    """
    if request.method == 'GET':
        # Render create-ticket template if GET request or if there was an error in submission data
        return render_template('create-ticket.html', Mode=Mode, user=current_user)

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
    openTickets = Ticket.query.filter(Ticket.status == Status.Open) # and (_now() - Ticket.time_created).total_seconds()/(60*60) < 24)
    claimedTickets = Ticket.query.filter(Ticket.status == Status.Claimed)
    closedTickets = Ticket.query.filter(Ticket.status == Status.Closed)
    loopNum = max(closedTickets.count(), max(openTickets.count(), claimedTickets.count()))

    # Get the user permission level here BEFORE attempting to load view-tickets page
    user_level = current_user.permission_level
    if(user_level < 2):
        flash('Insufficient permission level to view tickets', category='error')
        return redirect(url_for('auth.index'))

    return render_template('view_tickets.html', openTickets=list(openTickets), claimedTickets=list(claimedTickets), closedTickets=list(closedTickets), loopNum=loopNum, Status=Status, user=current_user)

@views.route('/update-ticket', methods=["GET", "POST"])
@login_required
def update_ticket():
    """
    This function handles the HTTP request when a tutor hits the claim, close, or reopen buttons on tickets
    :return: Render template to the original view-ticket.html page.
    """
    tutor = current_user
    ticketID = request.form.get("ticketID")

    openTickets = Ticket.query.filter(Ticket.status == Status.Open) # and (_now() - Ticket.time_created).total_seconds()/(60*60) < 24)
    claimedTickets = Ticket.query.filter(Ticket.status == Status.Claimed)
    closedTickets = Ticket.query.filter(Ticket.status == Status.Closed)
    loopNum = max(closedTickets.count(), max(openTickets.count(), claimedTickets.count()))

    print("RECIEVED TICKET ID: " + str(ticketID))
    print("VALUE OF ACTION: " + str(request.form.get("action")))
    # retrieve ticket by primary key using get()
    current_ticket = Ticket.query.get(ticketID)

    if request.form.get("action") == "Claim":
        # edit status of ticket to Claimed, assign tutor, set time claimed
        current_ticket.tutor_id = tutor.id
        current_ticket.status = Status.Claimed
        current_ticket.time_claimed = _now()
        print("TIME TICKET CLAIMED: " + str(_now()))
        db.session.commit()

        print("TUTOR ID THAT CLAIMED TICKET: " + str(current_ticket.tutor_id))
    elif request.form.get("action") == "Close":
        # edit status of ticket to CLOSED and set time closed on ticket
        current_ticket.status = Status.Closed
        current_ticket.time_closed = _now()
        print("TIME TICKET CLOSED: " + str(_now()))
        # calculate session duration from time claimed to time closed
        duration = _calc_session_duration(current_ticket.time_claimed, current_ticket.time_closed, current_ticket.session_duration)
        print("DURATION: " + str(duration))
        # TODO: get the duration calculation accounting for business days/hours too
        current_ticket.session_duration = duration
        db.session.commit()
    elif request.form.get("action") == "ReOpen":
        # edit status of ticket back to OPEN
        current_ticket.status = Status.Open
        db.session.commit()

    return render_template('view_tickets.html', openTickets=list(openTickets), claimedTickets=list(claimedTickets), closedTickets=list(closedTickets), loopNum=loopNum, Status=Status, user=current_user)

# TODO: Use flask-wtf for form handling and validation
def _attempt_create_ticket(form: ImmutableMultiDict):
    """
    Given an HTML form as an ImmutableMultiDict, extracts, strips, and verifies the following values :
        - email: must be non-empty
        - fullname: must be non-empty
        - assignment: must be non-empty
        - question: must be non-empty
        - mode: must be valid model.Mode

        returns a Ticket object if values are valid, None otherwise.
    """
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
        mode_val = _strip_or_none(form.get("mode"))
        mode = None

        try:
            if mode_val:
                mode = Mode(int(mode_val))

        except ValueError:
            flash('Could not submit ticket, must select a valid mode!', category='error')

        else:
            return Ticket(email, name, course, section, assignment, question, problem, mode)

def _strip_or_none(s: str):
    return s.strip() if s is not None else None

def _str_empty(s: str):
    return s is not None and not s

def _calc_session_duration(start_time, end_time, current_session_duration):
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

def _now():
    """
    Gets the current time in UTC.
    :return: Current time in Coordinated Universal Time (UTC)
    """
    return datetime.now()
