from flask import render_template, session, request, redirect, url_for
from flask import Blueprint
from .. import model as m
import datetime
from app.extensions import db

views = Blueprint('views', __name__)

def now():
    # gets the current time in UTC
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

@views.route('/view-tickets')
def view_tickets():
    #create some dummy tickets to display
    ticket1 = m.Ticket('test@test.com','clayton safranek','data structures','101','assignment1','idk how to turn my computer on','big big problem',now(),m.Status.Open,m.Mode.InPerson)
    ticket2 = m.Ticket('hellohello@test.com','john doe','basket weaving','101101','basket1','idk what a basket is','large problem',now(),m.Status.Claimed,m.Mode.InPerson)
    ticket3 = m.Ticket('goodbye@test.com','jane smith','claymation','4000','sculpting2','idk what clay is','massive problem',now(),m.Status.Closed,m.Mode.Online)
    #db.session.add(ticket1)
    #db.session.add(ticket2)
    #db.session.add(ticket3)
    db.session.commit()

    #get all tickets
    tickets = m.Ticket.query.all()
    print("TICKETS+++++++++++++ " + str(tickets))

    return render_template('view_tickets.html', tickets=tickets, m=m)
