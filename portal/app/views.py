from flask import render_template, request
from flask import Blueprint
from . import model as m
import datetime
from app import db

views = Blueprint('views', __name__)

def now():
    # gets the current time in UTC
    UTC = datetime.timezone.utc
    now = datetime.datetime.now(UTC)
    return now

@views.route('/')
def index():
    return render_template('home.html')

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
    assignment = request.form.get("assignmentNameField")
    question = request.form.get("specificQuestionField")
    problem = request.form.get("problemTypeField")
    print(f"Following ticket information has been created:\n{lastName}\n{firstName}\n{email}\n{course}\n{section}\n{assignment}\n{question}\n{problem}")

    # create ticket with info sent back
    if request.method == "POST":
        ticket = m.Ticket(
            email,
            firstName,
            lastName,
            course,
            section,
            assignment,
            question,
            problem,
            now())

        # insert into 'Tickets' table
        db.session.add(ticket)
        db.session.commit()

    return render_template('open-tickets.html', email=email, firstName=firstName, lastName=lastName, course=course,
                           section=section, assignmentName=assignment, specificQuestion=question, problemType=problem)

@views.route('/admin-login')
def admin_login():
    return render_template('admin-login.html')

@views.route('/tutor-login')
def tutor_login():
    return render_template('tutor-login.html')

@views.route('/student-login')
def student_login():
    return "Functionality to be implemented using Microsoft Authentication. This is just a placeholder button."
