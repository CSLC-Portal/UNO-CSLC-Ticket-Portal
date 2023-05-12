from flask import Blueprint
from flask import Response
from flask import request
from flask import flash
from flask import url_for
from flask import redirect
from flask import render_template

from app.model import ProblemType
from app.model import Ticket
from app.extensions import db
from flask_login import current_user

from app.model import User
from app.model import Course
from app.model import Message
from app.model import Permission
from app.model import Section
from app.model import Professor
from app.model import Semester
from app.model import SectionMode
from app.model import Season

from datetime import datetime

from app.extensions import db
from sqlalchemy.exc import IntegrityError

from app.util import str_empty
from app.util import strip_or_none
from app.util import permission_required
from app.util import build_days_of_week_string

import sys
import io

# https://owasp.org/www-community/attacks/CSV_Injection
from defusedcsv import csv

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/')
@permission_required(Permission.Admin)
def console():
    return render_template('admin-console.html')

@admin.route('/problems')
@permission_required(Permission.Admin)
def view_problem_types():
    problemTypes = ProblemType.query.all()
    return render_template('admin-problem-types.html', problemTypes=problemTypes, problemTypeCount=len(problemTypes))

@admin.route('/problems/add', methods=["POST"])
@permission_required(Permission.Admin)
def add_problem_type():
    problemType = strip_or_none(request.form.get("problemType"))

    try:
        if str_empty(problemType):
            flash('Could not create problem type, description must not be empty!', category='error')

        else:
            newCourse = ProblemType(problemType)
            db.session.add(newCourse)
            db.session.commit()
            flash('Problem type created successfully!', category='success')

    except IntegrityError:
        db.session.rollback()
        flash('Could not create problem type, invalid data!', category='error')

    except Exception as e:
        flash('Could not create problem type, unknown reason!', category='error')
        print(f'Could not create problem type, {e}', file=sys.stderr)

    return redirect(url_for('admin.view_problem_types'))

@admin.route('/problems/remove', methods=["POST"])
@permission_required(Permission.Admin)
def remove_problem_type():
    problemTypeID = strip_or_none(request.form.get("problemTypeID"))

    try:
        problemType: ProblemType = ProblemType.query.get(problemTypeID)

        if not problemType:
            flash('Could not delete problem type, problem type does not exist!', category='error')

        else:
            db.session.delete(problemType)
            db.session.commit()
            flash('Problem type successfully removed!', category='success')

    except IntegrityError:
        db.session.rollback()
        flash('Could not remove problem type, invalid data!', category='error')

    except Exception as e:
        flash('Could not remove problem type, unknown reason', category='error')
        print(f'Could not remove problem type: {e}', file=sys.stderr)

    return redirect(url_for('admin.view_problem_types'))

@admin.route('/problems/edit', methods=["POST"])
@permission_required(Permission.Admin)
def edit_problem_type():
    problemTypeID = strip_or_none(request.form.get("problemTypeID"))
    description = strip_or_none(request.form.get("description"))

    try:
        problemType: ProblemType = ProblemType.query.get(problemTypeID)

        if not problemType:
            flash('Could not update problem type, problem type does not exist!', category='error')

        elif str_empty(description):
            flash('Could not update problem type, description must not be empty!', category='error')

        else:
            problemType.problem_type = description
            db.session.commit()
            flash('Problem type successfully updated!', category='success')

    except IntegrityError:
        db.session.rollback()
        flash('Could not update problem type, invalid data!', category='error')

    except Exception as e:
        flash('Could not update problem type, unknown reason', category='error')
        print(f'Could not update problem type: {e}', file=sys.stderr)

    return redirect(url_for('admin.view_problem_types'))

@admin.route('/reports')
@permission_required(Permission.Admin)
def reports_form():
    return render_template('download-report.html')

@admin.route('/reports/download', methods=["POST"])
@permission_required(Permission.Admin)
def generate_reports():

    createDate = request.form.get("creationDate")
    courseName = strip_or_none(request.form.get("course"))

    if courseName:
        tickets = Ticket.query.filter(Ticket.time_created >= createDate, Ticket.course == courseName).all()

    else:
        tickets = Ticket.query.filter(Ticket.time_created >= createDate).all()

    header = [
        'Student Email', 'Student Name', 'Course', 'Section', 'Assignment Name', 'Specific Question', 'Problem Type', 'Time Created', 'Time Claimed',
        'Status', 'Time Closed', 'Session Duration', 'Mode', 'Tutor Notes', 'Tutor Id', 'Successful Session'
    ]

    with io.StringIO() as out:
        csv_writer = csv.writer(out)
        csv_writer.writerow(header)

        for ticket in tickets:
            # TODO: Will need to query course and section too!

            csv_writer.writerow([ ticket.student_email, ticket.student_name, ticket.course, ticket.section, ticket.assignment_name,
                                  ticket.specific_question, ticket.get_problem(), ticket.time_created, ticket.time_claimed, ticket.status,
                                  ticket.time_closed, ticket.mode, ticket.tutor_notes, ticket.tutor_id, ticket.successful_session ])

        payload = out.getvalue()

    return Response(payload, content_type='text/csv', headers={'Content-Disposition': 'attachment;filename=reports.csv'})

@admin.route('/tutors')
@permission_required(Permission.Admin)
def view_tutors():

    # NOTE: Cannot use inequality operators < > <= >= on enum from database as only
    #       the enum name is actually persisted.
    #
    return render_template('admin-tutors.html')

@admin.route('/tutors/add', methods=['POST'])
@permission_required(Permission.Admin)
def add_tutor():
    email = strip_or_none(request.form.get("email"))
    permission_val = strip_or_none(request.form.get("permission"))
    permission = None

    try:
        if permission_val:
            permission = Permission(int(permission_val))

        user: User = User.query.filter_by(email=email).one_or_none()

        if str_empty(email):
            flash('Email must not be empty!', category='error')

        elif permission and current_user.permission <= permission:
            flash('Cannot add user of higher or equal permission level as yourself!', category='error')

        elif user and user.permission > Permission.Student:
            flash('User already exists in the role hierarchy!', category='error')

        elif user and user.permission == Permission.Student:
            user.tutor_is_active = True
            user.permission = permission
            db.session.commit()
            flash('New user successfully added!', category='success')

        else:
            create_pseudo_super_user(email, permission)
            flash('New user successfully added!', category='success')

    except ValueError:
        flash('Could not add user, must select a valid mode!', category='error')

    except IntegrityError:
        db.session.rollback()
        flash('Could not add user, invalid data!', category='error')

    except Exception as e:
        flash('Could not add user, unknown reason!', category='error')
        print(f'Could not add user, {e}', file=sys.stderr)

    return redirect(url_for('admin.view_tutors'))

@admin.route('/tutors/remove', methods=['POST'])
@permission_required(Permission.Admin)
def remove_tutor():
    user_id = strip_or_none(request.form.get("userID"))

    try:
        user: User = User.query.get(user_id)

        if not user:
            flash('Could not remove user, user does not exist!', category='error')

        elif user == current_user:
            flash('You cannot remove yourself from the role hierarchy!', category='error')

        elif current_user.permission <= user.permission:
            flash('Cannot remove user of higher or equal permission level as yourself!', category='error')

        else:
            _attempt_delete_super_user(user)
            flash('User successfully removed!', category='success')

    except IntegrityError:
        db.session.rollback()
        flash('Could not remove user, invalid data!', category='error')

    except Exception as e:
        flash('Could not remove user, unknown reason', category='error')
        print(f'Failed to remove user: {e}', file=sys.stderr)

    return redirect(url_for('admin.view_tutors'))

@admin.route('/tutors/edit', methods=['POST'])
@permission_required(Permission.Admin)
def edit_tutor():
    user_id = strip_or_none(request.form.get("userID"))
    permission_val = strip_or_none(request.form.get("permission"))
    active = request.form.get("active") is not None

    try:
        user: User = User.query.get(user_id)

        new_permission = None
        if permission_val:
            new_permission = Permission(int(permission_val))

        if not user:
            flash('Could not update user, user does not exist!', category='error')

        elif user == current_user:
            flash('You cannot update yourself!', category='error')

        elif current_user.permission <= user.permission:
            flash('Cannot update user of higher or equal permission level as yourself!', category='error')

        elif new_permission and current_user.permission <= new_permission:
            flash('Cannot promote user to higher or equal permission level as yourself!', category='error')

        else:
            _attempt_edit_user(user, active, new_permission)
            flash('User successfully updated!', category='success')

    except ValueError:
        flash('Could not update user, input values invalid!', category='error')

    except IntegrityError:
        flash('Could not update user, invalid data!', category='error')

    except Exception as e:
        flash('Could not update user, unknown reason!', category='error')
        print(f'Could not update user, {e}', file=sys.stderr)

    return redirect(url_for('admin.view_tutors'))

@admin.route('/courses')
@permission_required(Permission.Admin)
def view_courses():
    # get all courses, just for validation in html
    courses = Course.query.all()
    return render_template('admin-course.html', courses=courses)

@admin.route('/courses/add', methods=["POST"])
@permission_required(Permission.Admin)
def add_course():

    courseDepartment = strip_or_none(request.form.get("courseDepartment"))
    courseNumber = strip_or_none(request.form.get("courseNumber"))
    courseName = strip_or_none(request.form.get("courseName"))
    displayOnIndex = request.form.get("displayOnIndex")

    # set on display
    displayOnIndex = displayOnIndex is not None

    # validate the input coming in. store everything in DB the same
    if str_empty(courseDepartment):
        flash('Could not create course, course department must not be empty!', category='error')

    elif str_empty(courseNumber):
        flash('Could not create course, course number must not be empty!', category='error')

    elif str_empty(courseName):
        flash('Could not create course, course name must not be empty!', category='error')

    else:
        # TODO: change this to query for department and num like CSCI 1234, cannot have duplicate ones of those
        tmpCourse = Course.query.filter_by(number=courseNumber, course_name=courseName).first()
        if tmpCourse is None:
            newCourse = Course(courseDepartment, courseNumber, courseName, displayOnIndex)
            db.session.add(newCourse)
            db.session.commit()
            flash('Course created successfully!', category='success')
            # TODO: return redirect for admin console home?
        else:
            flash('Course already exists in database!', category='error')

    return redirect(url_for('admin.view_courses'))

@admin.route('/courses/remove', methods=['POST'])
@permission_required(Permission.Admin)
def remove_course():

    course_id = strip_or_none(request.form.get("courseID"))

    try:
        course: Course = Course.query.get(course_id)

        if course:
            db.session.delete(course)
            db.session.commit()
            flash('Course successfully removed!', category='success')
        else:
            flash('Could not remove course, course does not exist!', category='error')

    except IntegrityError:
        db.session.rollback()
        flash('Could not remove course, invalid data!', category='error')

    except Exception as e:
        flash('Could not remove course, unknown reason', category='error')
        print(f'Failed to remove course: {e}', file=sys.stderr)

    return redirect(url_for('admin.view_courses'))

@admin.route('/courses/edit', methods=['POST'])
@permission_required(Permission.Admin)
def edit_course():
    course_id = strip_or_none(request.form.get("courseID"))
    newDept = strip_or_none(request.form.get("updateCourseDept"))
    newNum = strip_or_none(request.form.get("updateCourseNum"))
    newName = strip_or_none(request.form.get("updateCourseName"))

    try:
        course: Course = Course.query.get(course_id)

        # check if everything comes back all equal
        if course.course_name == newName and course.department == newDept and course.number == newNum:
            flash('No updates to course, attributes remain the same.', category='message')

        elif not course:
            flash('Could not update course, course does not exist!', category='error')

        elif str_empty(newDept):
            flash('Could not update course, department cannot be empty!', category='error')

        elif str_empty(newNum):
            flash('Could not update course, course number cannot be empty!', category='error')

        elif str_empty(newName):
            flash('Could not update course, course name cannot be empty!', category='error')

        elif course.course_name != newName and (course.department == newDept and course.number == newNum):
            # only update course name
            course.course_name = newName
            db.session.commit()
            flash("Course updated successfully!", category='success')
        else:
            tmpCourse = Course.query.filter_by(number=newNum, department=newDept).first()
            if tmpCourse is None:
                # check if new updated course will cause deuplicate
                if newDept != course.department:
                    course.department = newDept
                if newNum != course.number:
                    course.number = newNum
                if newName != course.course_name:
                    course.course_name = newName
                db.session.commit()
                flash("Course updated successfully!", category='success')
            else:
                flash('Could not update course, would cause duplicate courses in DB!', category='error')

    except ValueError:
        flash('Could not update Course, input values invalid!', category='error')

    except IntegrityError:
        flash('Could not update course, invalid data!', category='error')

    except Exception as e:
        flash('Could not update course, unknown reason!', category='error')
        print(f'Could not update course, {e}', file=sys.stderr)

    return redirect(url_for('admin.view_courses'))

@admin.route('/courses/toggle-display', methods=['POST'])
@permission_required(Permission.Admin)
def toggle_display():
    course_id = request.form.get("toggleID")
    try:
        course: Course = Course.query.get(course_id)
        # reverse whatever value it currently has for display
        if course.on_display:
            course.on_display = False
        else:
            course.on_display = True
        db.session.commit()

    except ValueError:
        flash('Could not toggle course display, input values invalid!', category='error')

    except IntegrityError:
        flash('Could not toggle course display, invalid data!', category='error')

    except Exception as e:
        flash('Could not toggle course display, unknown reason!', category='error')
        print(f'Could not toggle course, {e}', file=sys.stderr)
    return redirect(url_for('admin.view_courses'))

@admin.route('/semesters')
@permission_required(Permission.Admin)
def view_semesters():
    # get all courses, just for validation in html
    semesters = Semester.query.all()
    return render_template('admin-semester.html', semesters=semesters)

@admin.route('/semesters/add', methods=["POST"])
@permission_required(Permission.Admin)
def add_semester():

    year = strip_or_none(request.form.get("yearInput"))
    season = strip_or_none(request.form.get("seasonInput"))
    startDate = strip_or_none(request.form.get("startDate"))
    endDate = strip_or_none(request.form.get("endDate"))

    # validate input coming in
    if str_empty(year):
        flash('Could not create semester, year must not be empty!', category='error')

    elif str_empty(season):
        flash('Could not create semester, season must not be empty!', category='error')

    elif str_empty(startDate):
        flash('Could not create semester, start date must not be empty!', category='error')

    elif str_empty(endDate):
        flash('Could not create semester, end date must not be empty!', category='error')

    elif len(year) != 4:
        flash('Could not create semester, please enter valid year in the format YYYY!', category='error')

    else:
        # check if semester already exists in DB, impossible to have two summer 2023 semesters fo example
        tmpSemester = Semester.query.filter_by(season=season, year=year).first()
        if tmpSemester is None:
            # create semester and add it to DB, need to cast dates from string to date objects
            start = datetime.strptime(startDate, "%Y-%m-%d").date()
            end = datetime.strptime(endDate, "%Y-%m-%d").date()
            newSemester = Semester(year, season, start, end)
            db.session.add(newSemester)
            db.session.commit()
            flash('Semester created successfully!', category='success')

        else:
            flash("Semester '" + season + " " + year + "' already exists in database!", category='error')

    return redirect(url_for('admin.view_semesters'))

@admin.route('/semesters/remove', methods=['POST'])
@permission_required(Permission.Admin)
def remove_semester():

    semester_id = strip_or_none(request.form.get("semesterID"))

    try:
        semester: Semester = Semester.query.get(semester_id)

        if semester:
            db.session.delete(semester)
            db.session.commit()
            flash('Semester successfully removed!', category='success')

        else:
            flash('Could not remove semester, semester does not exist!', category='error')

    except IntegrityError:
        db.session.rollback()
        flash('Could not remove semester, invalid data!', category='error')

    except Exception as e:
        flash('Could not remove semester, unknown reason', category='error')
        print(f'Failed to remove semester: {e}', file=sys.stderr)

    return redirect(url_for('admin.view_semesters'))

@admin.route('/semesters/edit', methods=['POST'])
@permission_required(Permission.Admin)
def edit_semester():
    semester_id = strip_or_none(request.form.get("semesterID"))
    newYear = strip_or_none(request.form.get("yearUpdate"))
    newSeason = strip_or_none(request.form.get("seasonUpdate"))
    start = strip_or_none(request.form.get("updateStartDate"))
    end = strip_or_none(request.form.get("updateEndDate"))
    newStart = datetime.strptime(start, "%Y-%m-%d").date()
    newEnd = datetime.strptime(end, "%Y-%m-%d").date()

    try:
        semester: Semester = Semester.query.get(semester_id)

        if semester.year == int(newYear) and semester.season == Season[newSeason] and semester.start_date == newStart and semester.end_date == newEnd:
            flash('No updates to semester, attributes remain the same.', category='message')
        elif not semester:
            flash('Could not update semester, semester does not exist!', category='error')
        elif str_empty(newYear):
            flash('Could not update semester, year cannot be empty!', category='error')
        elif str_empty(newSeason):
            flash('Could not update semester, season cannot be empty!', category='error')
        elif str_empty(start):
            flash('Could not update semester, start date cannot be empty!', category='error')
        elif str_empty(end):
            flash('Could not update semester, end date cannot be empty!', category='error')
        else:
            tmpSemester = Semester.query.filter_by(season=newSeason, year=newYear).first()
            if tmpSemester is None:
                if newYear != semester.year:
                    semester.year = int(newYear)
                if Season[newSeason] != semester.season:
                    semester.season = Season[newSeason]
                if newStart != semester.start_date:
                    semester.start_date = newStart
                if newEnd != semester.end_date:
                    semester.end_date = newEnd
                db.session.commit()
                flash("Semester updated successfully!", category='success')
            elif tmpSemester is not None and (semester.start_date != newStart or semester.end_date != newEnd):
                semester.start_date = newStart
                semester.end_date = newEnd
                db.session.commit()
                flash("Semester updated successfully!", category='success')
            else:
                flash('Could not update semester, would cause duplicate semesters in DB!', category='error')

    except IntegrityError:
        db.session.rollback()
        flash('Could not update semester, invalid data!', category='error')

    except Exception as e:
        flash('Could not update semester, unknown reason', category='error')
        print(f'Failed to update semester: {e}', file=sys.stderr)

    return redirect(url_for('admin.view_semesters'))

@admin.route('/professors')
@permission_required(Permission.Admin)
def view_professors():
    # get all courses, just for validation in html
    professors = Professor.query.all()
    return render_template('admin-professor.html', professors=professors)

@admin.route('/professors/add', methods=["POST"])
@permission_required(Permission.Admin)
def add_professor():

    firstName = strip_or_none(request.form.get("firstNameInput"))
    lastName = strip_or_none(request.form.get("lastNameInput"))

    # validate input coming in
    if str_empty(firstName):
        flash('Could not add professor, first name must not be empty!', category='error')
    elif str_empty(lastName):
        flash('Could not add professor, last name must not be empty!', category='error')
    else:
        # check if professor already exists in DB, store all capitalized so checks against caps doesn't happen
        tmpProfessor = Professor.query.filter_by(first_name=firstName.capitalize(), last_name=lastName.capitalize()).first()
        if tmpProfessor is None:
            # create professor and add it to DB, store as capitalized
            newProfessor = Professor(firstName.capitalize(), lastName.capitalize())
            db.session.add(newProfessor)
            db.session.commit()
            flash('Professor added successfully!', category='success')
        else:
            flash("Professor '" + firstName.title() + " " + lastName.title() + "' already exists in database!", category='error')

    return redirect(url_for('admin.view_professors'))

@admin.route('/professors/remove', methods=['POST'])
@permission_required(Permission.Admin)
def remove_professor():

    professor_id = strip_or_none(request.form.get("professorID"))

    try:
        professor: Professor = Professor.query.get(professor_id)

        if professor:
            db.session.delete(professor)
            db.session.commit()
            flash('Professor successfully removed!', category='success')

        else:
            flash('Could not remove professor, professor does not exist!', category='error')

    except IntegrityError:
        db.session.rollback()
        flash('Could not remove professor, invalid data!', category='error')

    except Exception as e:
        flash('Could not remove professor, unknown reason', category='error')
        print(f'Failed to remove professor: {e}', file=sys.stderr)

    return redirect(url_for('admin.view_professors'))

@admin.route('/professors/edit', methods=['POST'])
@permission_required(Permission.Admin)
def edit_professor():
    professor_id = strip_or_none(request.form.get("professorID"))
    newFName = strip_or_none(request.form.get("fnameUpdate")).capitalize()
    newLName = strip_or_none(request.form.get("lnameUpdate")).capitalize()

    try:
        professor: Professor = Professor.query.get(professor_id)

        if professor.first_name == newFName and professor.last_name == newLName:
            flash('No updates to professor, attributes remain the same.', category='message')

        elif not professor:
            flash('Could not update professor, professor does not exist!', category='error')

        elif str_empty(newFName):
            flash('Could not update professor, first name cannot be empty!', category='error')

        elif str_empty(newLName):
            flash('Could not update professor, last name cannot be empty!', category='error')

        else:
            tmpProfessor = Professor.query.filter_by(first_name=newFName.capitalize(), last_name=newLName.capitalize()).first()
            if tmpProfessor is None:
                if newFName != professor.first_name:
                    professor.first_name = newFName.capitalize()
                if newLName != professor.last_name:
                    professor.last_name = newLName.capitalize()
                db.session.commit()
                flash("Professor updated successfully!", category='success')
            else:
                flash('Could not update professor, would cause duplicate professors in DB!', category='error')

    except IntegrityError:
        db.session.rollback()
        flash('Could not update professor, invalid data!', category='error')

    except Exception as e:
        flash('Could not update professor, unknown reason', category='error')
        print(f'Failed to update professor: {e}', file=sys.stderr)

    return redirect(url_for('admin.view_professors'))

@admin.route('/sections')
@permission_required(Permission.Admin)
def view_sections():
    # get all courses, just for validation in html
    sections = Section.query.all()
    semesters = Semester.query.all()
    courses = Course.query.all()
    professors = Professor.query.all()
    return render_template('admin-sections.html', sections=sections, semesters=semesters, courses=courses, professors=professors, SectionMode=SectionMode)

@admin.route('/sections/add', methods=["POST"])
@permission_required(Permission.Admin)
def add_section():

    semester = strip_or_none(request.form.get("semesterInput"))
    course = strip_or_none(request.form.get("courseInput"))
    sectionNum = strip_or_none(request.form.get("sectionNumberInput"))
    sectionMode = strip_or_none(request.form.get("mode"))
    monInput = strip_or_none(request.form.get("mondayTime"))
    tueInput = strip_or_none(request.form.get("tuesdayTime"))
    wedInput = strip_or_none(request.form.get("wednesdayTime"))
    thuInput = strip_or_none(request.form.get("thursdayTime"))
    friInput = strip_or_none(request.form.get("fridayTime"))
    secStartTime = strip_or_none(request.form.get("sectionStartTime"))
    secEndTime = strip_or_none(request.form.get("sectionEndTime"))
    professor = strip_or_none(request.form.get("professorInput"))

    # validate input coming in
    if monInput is None and tueInput is None and wedInput is None and thuInput is None and friInput is None and sectionMode != "TotallyOnline":
        flash('Could not create section, must provide atleast one day of the week for section if mode is ' + str(sectionMode) + '!', category='error')
    elif (sectionMode == "Remote" or sectionMode == "InPerson") and (secStartTime == "" or secEndTime == ""):
        flash('Could not create section, must provide both start and end time for section if mode is ' + str(sectionMode) + '!', category='error')
    else:
        # check if section already exists in DB
        tmpSection = Section.query.filter_by(section_number=sectionNum, course_id=course).first()
        if tmpSection is None:
            # create section and add it to DB
            # need to assemble days of week string to set in DB
            daysOfWeek = ""
            if sectionMode != "TotallyOnline":
                daysOfWeek = build_days_of_week_string(monInput, tueInput, wedInput, thuInput, friInput)

            # need to assemble python time object to set in db
            try:
                if secStartTime is not None:
                    secStartTime = datetime.strptime(secStartTime, '%H:%M').time()

                if secEndTime is not None:
                    secEndTime = datetime.strptime(secEndTime, '%H:%M').time()

            except ValueError:
                # start and end dates are empty strings because mode = totally online. set time to 00:00
                # secStartTime = datetime.strptime("00:00:00", '%H:%M:%S').time()
                # secEndTime = datetime.strptime("00:00:00", '%H:%M:%S').time()
                secStartTime = None
                secEndTime = None

            newSection = Section(sectionNum, daysOfWeek, secStartTime, secEndTime, sectionMode, course, semester, professor)
            db.session.add(newSection)
            db.session.commit()
            flash('Section added successfully!', category='success')
        else:
            flash(f'The section already exists in this course!', category='error')

    return redirect(url_for('admin.view_sections'))

@admin.route('/sections/remove', methods=['POST'])
@permission_required(Permission.Admin)
def remove_section():

    section_id = strip_or_none(request.form.get("sectionID"))

    try:
        section: Section = Section.query.get(section_id)

        if section:
            db.session.delete(section)
            db.session.commit()
            flash('Section successfully removed!', category='success')

        else:
            flash('Could not remove section, section does not exist!', category='error')

    except IntegrityError:
        db.session.rollback()
        flash('Could not remove section, invalid data!', category='error')

    except Exception as e:
        flash('Could not remove section, unknown reason', category='error')
        print(f'Failed to remove section: {e}', file=sys.stderr)

    return redirect(url_for('admin.view_sections'))

@admin.route('/sections/edit', methods=['POST'])
@permission_required(Permission.Admin)
# flake8: noqa: C901
def edit_section():
    section_id = strip_or_none(request.form.get("sectionID"))
    newSemester = strip_or_none(request.form.get("semesterUpdate"))
    newCourse = strip_or_none(request.form.get("updateCourse"))
    newSectionNum = strip_or_none(request.form.get("updateSectionNum"))
    updateMode = strip_or_none(request.form.get("updateMode"))
    updateMon = strip_or_none(request.form.get("updateMon"))
    updateTue = strip_or_none(request.form.get("updateTue"))
    updateWed = strip_or_none(request.form.get("updateWed"))
    updateThu = strip_or_none(request.form.get("updateThu"))
    updateFri = strip_or_none(request.form.get("updateFri"))
    updateProf = strip_or_none(request.form.get("updateProf"))

    try:
        section: Section = Section.query.get(section_id)

        start = strip_or_none(request.form.get("updateStart"))
        if start is not None and not str_empty(start):
            try:
                start = datetime.strptime(start, '%H:%M:%S').time()
            except ValueError:
                # incoming time change
                start = datetime.strptime(start, '%H:%M').time()
        else:
            # empty string came back, set to None
            start = None
        end = strip_or_none(request.form.get("updateEnd"))
        if end is not None and not str_empty(end):
            try:
                end = datetime.strptime(end, '%H:%M:%S').time()
            except ValueError:
                # incoming time change
                end = datetime.strptime(end, '%H:%M').time()
        else:
            # empty string came back, set to None
            end = None

        if _any_change_in_data(section, newSemester, newCourse, newSectionNum, updateMode, updateMon, updateTue, updateWed, updateThu,
           updateFri, updateProf, start, end):
            flash('No updates to section, attributes remain the same.', category='message')

        elif (section.start_time != start or section.end_time != end) and updateMode == "TotallyOnline":
            flash('Could not update section, cannot have start/end times with online class!', category='error')

        elif not _no_days_of_week(updateMon, updateTue, updateWed, updateThu, updateFri) and updateMode == "TotallyOnline":
            flash('Could not update section, cannot have days of week with online class!', category='error')

        elif (updateMode == "Remote" or updateMode == "InPerson") and _no_days_of_week(updateMon, updateTue, updateWed, updateThu, updateFri):
            flash('Could not update section, atleast one day of the week is required if modes are In Person or Remote!', category='error')

        elif (updateMode == "Remote" or updateMode == "InPerson") and (start == "" or start is None or end == "" or end is None):
            flash('Could not update section, start/end times required if modes are In Person or Remote!', category='error')

        elif not _any_change_in_data(section, newSemester, newCourse, newSectionNum, updateMode, updateMon, updateTue, updateWed, updateThu,
                                     updateFri, updateProf, start, end) and (section.course_id == int(newCourse) and section.section_number == int(newSectionNum)):
            # update everything else
            _attempt_update_section(section, newSemester, newCourse, newSectionNum, updateMode, updateMon, updateTue, updateWed, updateThu,
                                    updateFri, updateProf, start, end)
            flash("Section updated successfully!", category='success')

        else:
            tmpSection = Section.query.filter_by(section_number=newSectionNum, course_id=newCourse).first()
            if tmpSection is None:
                # update everything
                _attempt_update_section(section, newSemester, newCourse, newSectionNum, updateMode, updateMon, updateTue, updateWed, updateThu,
                                        updateFri, updateProf, start, end)
                # db.session.commit()
                flash("Section updated successfully!", category='success')
            else:
                flash('Could not update section, would cause duplicate sections in DB!', category='error')
    except IntegrityError:
        db.session.rollback()
        flash('Could not update section, invalid data!', category='error')

    except Exception as e:
        flash('Could not update section, unknown reason', category='error')
        print(f'Failed to update section: {e}', file=sys.stderr)

    return redirect(url_for('admin.view_sections'))

@admin.route('/messages')
@permission_required(Permission.Admin)
def view_messages():
    # get all courses, just for validation in html
    messages = Message.query.all()
    return render_template('admin-messages.html', messages=messages)

@admin.route('/messages/add', methods=["POST"])
@permission_required(Permission.Admin)
def add_message():

    message = strip_or_none(request.form.get("message"))
    startDate = datetime.strptime(request.form.get("startDate"), "%Y-%m-%d")
    endDate = datetime.strptime(request.form.get("endDate"), "%Y-%m-%d")
    print("MESSAGE: " + str(message))
    print("START DATE: " + str(startDate))
    print("END DATE: " + str(endDate))

    newMessage = Message(message, startDate, endDate)
    db.session.add(newMessage)
    db.session.commit()
    flash('Message added successfully!', category='success')

    return redirect(url_for('admin.view_messages'))

@admin.route('/messages/remove', methods=["POST"])
@permission_required(Permission.Admin)
def remove_message():
    message_id = strip_or_none(request.form.get("messageID"))
    try:
        message: Message = Message.query.get(message_id)

        if not message:
            flash('Could not remove message, message does not exist!', category='error')

        else:
            db.session.delete(message)
            db.session.commit()
            flash('message successfully removed!', category='success')

    except IntegrityError:
        db.session.rollback()
        flash('Could not remove message, invalid data!', category='error')

    except Exception as e:
        flash('Could not remove message, unknown reason', category='error')
        print(f'Failed to remove message: {e}', file=sys.stderr)

    return redirect(url_for('admin.view_messages'))

def create_pseudo_super_user(email: str, permission: Permission):
    """
    If the user doesn't exist, creates and inserts an 'incomplete' user into the database given an email and permission level.
    When the user signs in using their email, the remaining info will be automatically updated in the database.

    If the user exist, the the permission level is updated for the user.
    """

    pseudo_user = User(None, permission, email, None, True, False)
    db.session.add(pseudo_user)
    db.session.commit()

def _attempt_delete_super_user(user: User):
    """
    If the user is complete then their permissions will be set to the lowest level.
    However, they will remain in the database and past information will be retained.

    If the user is not complete then they will be removed from the database.
    """

    # The user was never completed, we can delete this record
    if not user.is_complete():
        db.session.delete(user)

    else:
        user.tutor_is_active = False
        user.permission = Permission.Student

    db.session.commit()

def _attempt_edit_user(user: User, active, permission=None):
    try:
        if permission:
            user.permission = permission

        user.tutor_is_active = active
        db.session.commit()

    except IntegrityError as e:
        db.session.rollback()
        raise e

def _any_change_in_data(sec, semester, course, sectionNum, sectionMode, mon, tue, wed, thu, fri, professor, start, end):
    # calc days of week
    days = build_days_of_week_string(mon, tue, wed, thu, fri)

    return sec.section_number == int(sectionNum) and \
           sec.days_of_week == days and \
           sec.section_mode == SectionMode[sectionMode] and \
           sec.course_id == int(course) and \
           sec.semester_id == int(semester) and \
           sec.professor_id == int(professor) and \
           sec.start_time == start and \
           sec.end_time == end

def _no_days_of_week(m, t, w, th, f):
    if m is None and t is None and w is None and th is None and f is None:
        return True
    return False

def _attempt_update_section(sec, semester, course, sectionNum, sectionMode, mon, tue, wed, thu, fri, professor, start, end):
    days = build_days_of_week_string(mon, tue, wed, thu, fri)

    # update everything that needs updating
    if sec.section_number != int(sectionNum):
        sec.section_number = int(sectionNum)
    if sec.days_of_week != days:
        sec.days_of_week = days
    if sec.section_mode != SectionMode[sectionMode]:
        sec.section_mode = sectionMode
    if sec.course_id != int(course):
        sec.course_id = course
    if sec.semester_id != int(semester):
        sec.semester_id = semester
    if sec.professor != int(professor):
        sec.professor_id = professor
    if sec.start_time != start:
        sec.start_time = start
    if sec.end_time != end:
        sec.end_time = end
    db.session.commit()

def _get_start_time(start):
    if start is not None and not str_empty(start):
        try:
            start = datetime.strptime(start, '%H:%M:%S').time()
        except ValueError:
            # incoming time change
            start = datetime.strptime(start, '%H:%M').time()
    else:
        # empty string came back, set to None
        start = None
