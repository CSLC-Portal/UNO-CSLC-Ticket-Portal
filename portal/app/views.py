from flask import Blueprint
from . import model as m
import datetime
from app import db

views = Blueprint('views', __name__)
from flask import render_template, request

def now():
    #gets the current time in UTC
    UTC = datetime.timezone.utc
    now = datetime.datetime.now(UTC)
    return now

@views.route('/')
def index():
    return 'Future site of the CSLC Tutoring Portal!'

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

