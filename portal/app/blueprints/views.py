from flask import Blueprint
from .. import model as m
import datetime
from app import db
from flask import render_template, session, request, redirect, url_for

views = Blueprint('views', __name__)

def now():
    #gets the current time in UTC
    UTC = datetime.timezone.utc
    now = datetime.datetime.now(UTC)
    return now

@views.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("auth.login"))

    return render_template('index.html', user=session["user"])

@views.route('/create-ticket')
def create_ticket():
    return render_template('create-ticket.html')

@views.route('/open-tickets', methods=["POST"])
def open_tickets():
    email = request.form.get("emailAdressField")
    firstName = request.form.get("firstNameField")
    lastName = request.form.get("lastNameField")
    course = request.form.get("courseField")
    section = request.form.get("sectionField")
    assignmentName = request.form.get("assignmentNameField")
    specificQuestion = request.form.get("specificQuestionField")
    problemType = request.form.get("problemTypeField")
    print("Following ticket information has been created:\n %s\n %s\n %s\n %s\n %s\n %s\n %s\n %s\n" % (lastName, firstName, email, course, section, assignmentName, specificQuestion, problemType))

    #create ticket with info sent back
    if request.method == "POST":
        ticket = m.Ticket(
            email,
            firstName,
            lastName,
            course,
            section,
            assignmentName,
            specificQuestion,
            problemType,
            now()
            )
        #insert into 'Tickets' table
        db.session.add(ticket)
        db.session.commit()

    return render_template('open-tickets.html', email=email, firstName=firstName, lastName=lastName, course=course,
                           section=section, assignmentName=assignmentName, specificQuestion=specificQuestion, problemType=problemType)
