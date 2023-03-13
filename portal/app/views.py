from flask import Blueprint

views = Blueprint('views', __name__)
from flask import render_template, request

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
    return render_template('open-tickets.html', email=email, firstName=firstName, lastName=lastName, course=course,
                           section=section, assignmentName=assignmentName, specificQuestion=specificQuestion, problemType=problemType)
