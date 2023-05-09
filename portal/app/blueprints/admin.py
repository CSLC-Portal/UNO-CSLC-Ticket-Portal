from flask import Blueprint, Response, send_from_directory
from flask import request
from flask import flash
from flask import url_for
from flask import redirect
from flask import render_template
import csv
import os
import io

from app.model import ProblemTypes
from app.model import Ticket
from app.extensions import db
import datetime
admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/')
def console():
    return render_template('admin-console.html')

def _strip_or_none(s: str):
    return s.strip() if s is not None else None

def _str_empty(s: str):
    return s is not None and not s

@admin.route('/problems', methods=["GET", "POST"])
def add_problem_type():
    if request.method == "POST":
        problemType = _strip_or_none(request.form.get("problemType"))
        print("PROBLEM TYPE: " + str(problemType))

        # validate the input coming in. store everything in DB the same
        if _str_empty(problemType):
            flash('Could not create problem Type, problem type must not be empty!', category='error')
        else:
            tmpCourse = ProblemTypes.query.filter_by(problem_type=problemType).first()
            if tmpCourse is None:
                newCourse = ProblemTypes(problemType)
                db.session.add(newCourse)
                db.session.commit()
                flash('Problem Type created successfully!', category='success')
                # TODO: return redirect for admin console home?
            else:
                flash('Problem Type already exists in database!', category='error')
                print("Problem Type ALREADY IN DB!")

    problemTypes = ProblemTypes.query.all()
    return render_template('admin-problem-types.html', problemTypes=problemTypes)

@admin.route('/download', methods=["GET", "POST"])
def download_report():

    createDate = request.form.get("creationDate")
    closeDate = request.form.get("closedDate")

    courseName = _strip_or_none(request.form.get("course"))

    if courseName:
        sub = Ticket.query.filter(Ticket.time_created >= createDate, Ticket.time_closed <= closeDate, Ticket.course == courseName).all()
    else:
        sub = Ticket.query.filter(Ticket.time_created >= createDate, Ticket.time_closed <= closeDate).all()

    global format
    format = [
        ['Student Email', 'Student Name', 'Course', 'Section', 'Assignment Name', 'Specific Question', 'Problem Type', 'Time Created', 'Time Claimed',
         'Status', 'Time Closed', 'Session Duration', 'Mode', 'Tutor Notes', 'Tutor Id', 'Successful Session']
    ]
    ticketList = list(sub)
    lengthTickets = len(ticketList)

    for i in range(len(ticketList)):
        format.append([ticketList[i].student_email, ticketList[i].student_name, ticketList[i].course, ticketList[i].section, ticketList[i].assignment_name, 
                       ticketList[i].specific_question, ticketList[i].problem_type, ticketList[i].time_created, ticketList[i].time_claimed,
                       ticketList[i].status, ticketList[i].time_closed, ticketList[i].session_duration, ticketList[i].mode, ticketList[i].tutor_notes, 
                       ticketList[i].tutor_id, ticketList[i].successful_session])

    if request.method == "POST":
        start = request.form.get("creationDate")
        end = _strip_or_none(request.form.get("closedDate"))

        print(start)
        print(end)

    return render_template('download-report.html', sub=sub, lengthTickets=lengthTickets)


@admin.route('/download_csv', methods=["GET", "POST"])
def download_csv():
    file = io.StringIO()
    writer = csv.writer(file)
    for line in format:
        writer.writerow(line)

    return Response(file.getvalue(), content_type='text/csv', headers={'Content-Disposition': 'attachment;filename=cslc_report.csv'})


def fix_dde(cell):
    '''
    Handles a vulnerability with embedded formulae in csv files
    '''
    if cell is not None:
        cell = str(cell)
        if cell.startswith(('=', '+', '-', '@')):
            cell = "' " + cell
        cell = cell.rstrip()
    return cell