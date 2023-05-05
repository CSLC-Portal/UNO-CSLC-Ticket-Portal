from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Boolean
from sqlalchemy import Text

from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from .extensions import db
from flask_login import UserMixin

import datetime
import enum

Base = declarative_base(name='Base')

class ToStrEnum(enum.Enum):
    """
    Class that overrides the __str__ method to return only the name of the enum.
    """
    def __str__(self) -> str:
        return self.name

class Status(ToStrEnum):
    """
    This Status class is designed to mimic an enum for values of which a ticket can obtain for its status value.
    A ticket can have the following three status values: Open, Claimed, or Closed. As shown below as well.
    """
    Open = 1
    Claimed = 2
    Closed = 3

class Mode(ToStrEnum):
    """
    Mode class is designed to mimic an enum for values of which a ticket can be submitted.
    A ticket can either be submitted for online or inperson help. As shown below.
    """
    Online = 1
    InPerson = 2

class Permission(ToStrEnum):
    """
    The Permission class is designed to mimic an enum for different permission levels that a User might have.
    The available permission levels are either: student, tutor, or admin
    """
    Student = 1
    Tutor = 2
    Admin = 3

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def __le__(self, other):
        return self.value <= other.value

    def __ge__(self, other):
        return self.value >= other.value

class Season(ToStrEnum):
    """
    The Season class is designed to mimic an enum for different season types that are used in creation of a Semester.
    The available season options are the seasons for college semesters: Spring, Summer, Fall, and potentially J-Term
    """
    JTerm = 1
    Spring = 2
    Summer = 3
    Fall = 4

class User(db.Model, UserMixin):
    """
    The User class is the main model for every user that interacts with the CSLC Portal. In general there are only
    three types ofusers: students, tutuors, and admins. In order to determine what user is what, we have added a field
    called 'permission' which specifies which type of user the user object is. For example, a student User would have
    permission level of 1, tutor a permission level of 2, and an admin a permission level of 3. This way we can restrict what certain
    users are able to do on the CSLC portal like adding/modifying tutors, viewing ticket data, generating reports, etc
    """
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True, doc='Autonumber primary key for the users table.')
    oid = Column(String(50), unique=True, doc='ID token returned for the requestor. This is returned from MS authentication')
    permission = Column(Enum(Permission), nullable=False, doc='Specifies permission level of user')
    email = Column(String(120), unique=True, nullable=False, doc='Email of user')
    name = Column(String(120), doc='Users name')
    tutor_is_active = Column(Boolean, doc='T/F if the tutor is currently employed')
    tutor_is_working = Column(Boolean, doc='T/F if the tutor is currently working')
    tickets = db.relationship('Ticket', backref='user')

    def __init__(self, oidIn, permLevelIn, emailIn, nameIn, isActiveIn, isWorkingIn):
        self.oid = oidIn
        self.permission = permLevelIn
        self.email = emailIn
        self.name = nameIn
        self.tutor_is_active = isActiveIn
        self.tutor_is_working = isWorkingIn

    def is_complete(self):
        """
        Indicates whether or not this user is completed.
        Incomplete users could result from creating entries with only partial data
        """
        return self.oid is not None

    @staticmethod
    def get_tutors():
        # TODO: Cannot use inequality operators < > <= >= on enum from database as only
        #       the enum name is actually persisted. Find a way around this while keeping enum column?
        return User.query.filter(((User.permission == Permission.Tutor) | (User.permission == Permission.Admin)) & (User.oid != None))

    @staticmethod
    def get_pending():
        return User.query.filter(User.oid == None)

    @staticmethod
    def get_students():
        return User.query.filter(User.permission == Permission.Student)

    @staticmethod
    def get_admins():
        return User.query.filter(User.permission == Permission.Admin)

    def __repr__(self):
        return f'{self.name} ({self.email})'

class Ticket(db.Model):
    """
    The Ticket class is the main Model for the ticket objects that get created when students create and submit thier tickets for help.
    Every time a ticket is created, the student will only actualy enter in the following information:
    student_email, student_name, course, seciton, assignment_name, specific_question, and problem_type.
    The rest of the data fields are used in backoffice processing.
    """
    __tablename__ = 'Tickets'

    id = Column(Integer, primary_key=True, doc='Autonumber primary key for the ticket table.')
    student_email = Column(String(120), nullable=False, doc='Email of the student making the ticket.')
    student_name = Column(String(120), doc='The name of student making the ticket.')

    # TODO: Need to update these columns to be foreign keys the respective tabels
    course = Column(String(120), doc='The specific course this ticket issue is related to.')
    section = Column(String(120), doc='Course section ticket issue is relating to.')
    #

    assignment_name = Column(String(120), doc='Assignment the student needs help with.')
    specific_question = Column(Text, doc='Student question about the assignment.')
    problem_type = Column(String(120), doc='Type of problem the student is having.')
    time_created = Column(DateTime(True), nullable=False, doc='Time the ticket was created.', default=func.now())
    time_claimed = Column(DateTime(True), doc='Time the ticket was claimed by tutor.')
    time_closed = Column(DateTime(True), doc='Time the tutor marked the ticket as closed.')
    status = Column(Enum(Status), doc='Status of the ticket. 1=open, 2=claimed, 3=closed.', default=Status.Open)
    mode = Column(Enum(Mode), doc='Specifies whether the ticket was made for online or in-person help.')
    tutor_notes = Column(Text, doc='Space for tutors to write notes about student/ticket session.', default="")
    tutor_id = Column(Integer, db.ForeignKey('Users.id'), doc='Foreign key to the tutor who claimed this ticket.')
    successful_session = Column(Boolean, doc='T/F if the tutor was able to help the student with issue on ticket')
    # session_duration = Column(Time(True), doc='Amount of time the tutor spent on the ticket/student.')

    def __init__(self, sEmailIn, sNameIn, crsIn, secIn, assgnIn, quesIn, prblmIn, modeIn):
        self.student_email = sEmailIn
        self.student_name = sNameIn
        self.course = crsIn
        self.section = secIn
        self.assignment_name = assgnIn
        self.specific_question = quesIn
        self.problem_type = prblmIn
        self.mode = modeIn

    def claim(self, tutor: User):
        self.tutor_id = tutor.id
        self.status = Status.Claimed
        self.time_claimed = datetime.datetime.now()

    def close(self):
        self.status = Status.Closed
        self.time_closed = datetime.now()

    def reopen(self):
        self.status = Status.Open

    def calc_duration_open(self):
        if self.time_claimed is None:
            return datetime.datetime.now() - self.time_created

        return self.time_claimed - self.time_created

    def calc_duration_claimed(self):
        if self.time_claimed is None:
            return 0  # Ticket hasn't been claimed yet

        if self.time_closed is None:
            return datetime.datetime.now() - self.time_claimed

        return self.time_closed - self.time_claimed

    def __repr__(self):
        return f'Ticket: {self.specific_question} ({self.student_name})'

class Message(db.Model):
    """
    The Messages class is the main model for storing messages that the CSLC admins put in place to be displayed on the website.
    Each message has a string message, a start date, and an end date. This way the admins are able to specify a certain length of
    time for the message to be displayed and the admins do not have to worry about messages hanging around forever as they will
    eventually "expire" past the end date.
    """
    __tablename__ = 'Messages'

    id = Column(Integer, primary_key=True, doc='Autonumber primary key for the Messages table')
    message = Column(Text, doc='The text of the message to be displayed.')
    start_date = Column(DateTime(True), nullable=False, doc='The start date for the duration of the message to be displayed.')
    end_date = Column(DateTime(True), nullable=False, doc='The end date for the duration of the message to be displayed.')

    def __init__(self, messageIn, startIn, endIn):
        self.message = messageIn
        self.start_date = startIn
        self.end_date = endIn

    def __repr__(self):
        return f'{self.message} ({self.start_date})'

class ProblemType(db.Model):
    """
    The ProblemTypes class is the main model for storing the different problem types that the admins and tutors would like to configure.
    The problem types themselves are set in the ticket creation process by the students creating the tickets. This table models the options
    for different problem types that are available for students to choose from.
    """
    __tablename__ = 'ProblemTypes'

    id = Column(Integer, primary_key=True, doc='Autonumber primary key for the ProblemTypes table.')
    problem_type = Column(Text, doc='The description of the problem type - defined by admin or tutor.')
    # TODO: might want to add relationship to tickets value 'problem_type', something like this:
    # tickets = db.relationship('Ticket', backref='prblm_type')

    def __init__(self, prblmIn):
        self.problem_type = prblmIn

class Course(db.Model):
    """
    The Courses class is the main model for storing the different courses that are available for assistence within the tutoring center. The
    courses that are in this table are defined and populated by admins (and possibly tutors too).
    """
    __tablename__ = 'Courses'

    id = Column(Integer, primary_key=True, doc='Autonumber primary key for the Courses table.')
    department = Column(String(10), nullable=False, doc='The department abreviation for a class. E.g., CSCI, IST, etc.')
    number = Column(String(25), nullable=False, doc='The course number for a class. E.g., 4970')
    course_name = Column(String(50), nullable=False, doc='The name of the course itself. E.g., Operating Systems, Java II, etc.')
    on_display = Column(Boolean, doc="T/F if course should be displayed in available courses. This way admin does not need to keep adding/deleting a course.")
    sections = db.relationship('Section', backref='course')
    # TODO: add in tutors relationship and tickets relationship

    def __init__(self, depIn, numIn, nameIn, displayIn):
        self.department = depIn
        self.number = numIn
        self.course_name = nameIn
        self.on_display = displayIn

    def __repr__(self):
        return f'{self.department} {self.number}, {self.course_name}, {self.on_display}, Sections: {self.sections}'

class Section(db.Model):
    """
    The Sections class is the model for storing the different sections of courses that are available for assistence within the tutoring center.
    Different sections could be taught by different professors. Different sections are also taught at different times of the year. An example of
    a section would be '850' in the following course listing: "CSCI 4970-850".
    """
    __tablename__ = 'Sections'

    id = Column(Integer, primary_key=True, doc='Autonumber primary key for the Sections table.')
    section_number = Column(Integer, doc='The section numebr associated with a course number. E.g., 001, 850, etc.')
    time = Column(String(50), doc='The course meeting time. E.g. MW 1:00PM')
    course_id = Column(Integer, db.ForeignKey('Courses.id'), doc='The corresponding course a section is associated with.')
    semester_id = Column(Integer, db.ForeignKey('Semesters.id'), doc='The semester in which a section is offered during.')
    professor_id = Column(Integer, db.ForeignKey('Professors.id'), doc='Specific professor that teaches a particular session.')
    # TODO: potentially add relationship to semesters, professors, and tickets

    def __init__(self, secIn, timeIn):
        self.section_number = secIn
        self.time = timeIn

class Professor(db.Model):
    """
    The Professors class is the model for representing different professors that teach various courses.
    """
    __tablename__ = 'Professors'

    id = Column(Integer, primary_key=True, doc='Autonumber primary key for the Professors table.')
    first_name = Column(String(50), nullable=False, doc='First name of professor.')
    last_name = Column(String(50), nullable=False, doc='Last name of professor.')
    sections = db.relationship('Section', backref='professor')

    def __init__(self, firstIn, lastIn):
        self.first_name = firstIn
        self.last_name = lastIn

class Semester(db.Model):
    """
    The Semesters class is used to model the different pieces of information that represent a college Semester. Each semester has
    a year, season, start date, and an end date. For example: Spring 2023 (which has a start date of Jan 26, and an end date of May 15).
    Semesters are used in conjunction with course sections and classes that occur within semesters. Semesters might also be used with
    generating reports, as it provides a time frame for the admins to look at CSLC ticket data by semester.
    """
    __tablename__ = 'Semesters'

    id = Column(Integer, primary_key=True, doc='Autonumber primary key for the Semesters table.')
    year = Column(Integer, nullable=False, doc='The year of the semester. E.g., 2023.')
    season = Column(Enum(Season), nullable=False, doc='The season of the semester. E.g., Fall')
    start_date = Column(DateTime(True), nullable=False, doc='The start date, or first day, of a semester.')
    end_date = Column(DateTime(True), nullable=False, doc='The end date, or last day, of a semester.')
    sections = db.relationship('Section', backref='semester')

    def __init__(self, yearIn, seasonIn, startIn, endIn):
        self.year = yearIn
        self.season = seasonIn
        self.start_date = startIn
        self.end_date = endIn

class CanTutor(db.Model):
    """
    The CanTutor table is a join table that matches tutors and the available courses that they are able to tutor.
    For example, say John is a tutor with ID one, and he can tutor courses: A, B, and C. This table will join the
    tutor John and the list of courses that he can tutor.
    """
    __tablename__ = 'CanTutor'

    # id = Column(Integer, doc='Autonumber primary key for the CanTutor table.')
    tutor = Column(Integer, db.ForeignKey('Users.id'), primary_key=True, doc='The tutor that is able to tutor a course.')
    courses = Column(Integer, db.ForeignKey('Courses.id'), doc='Possible courses that a tutor can tutor.')

class Config(db.Model):
    """
    The Config table is really just a table that stands alone so it can house all of the miscelaneous configuration items that
    an admin might want to set for the tutoring center. For example, the hours of the tutoring center. Another thing that is currently
    stored as of now is the zoom link for the tutoring center. If any more miscelaneous infomraiton needs to be stored in the future a column
    can be added to this table to house it. As a future upgrade it would be nice to get this migrated to a configuration.json file that is just
    read from and written to in the browser that way we do not havea flat relational table, with no relations.
    """
    __tablename__ = 'Config'

    # need to have a primary key so just creating ID, will most liekly not be used
    id = Column(Integer, primary_key=True, doc='Autonumber primary key for the Config table.')
    zoom_link = Column(String(255), doc='The zoom link for the tutoring center.', default="zoom.us")
    # below are the hours for the tutring center, start/stop time for each day
    mon_start = Column(DateTime(True), doc='Start time for Mondays', default=datetime.time(hour=8, minute=0))
    mon_end = Column(DateTime(True), doc='End time for Mondays', default=datetime.time(hour=16, minute=0))
    tue_start = Column(DateTime(True), doc='Start time for Tuesdays', default=datetime.time(hour=8, minute=0))
    tue_end = Column(DateTime(True), doc='End time for Tuesdays', default=datetime.time(hour=16, minute=0))
    wed_start = Column(DateTime(True), doc='Start time for Wednesdays', default=datetime.time(hour=8, minute=0))
    wed_end = Column(DateTime(True), doc='End time for Wednesdays', default=datetime.time(hour=16, minute=0))
    thur_start = Column(DateTime(True), doc='Start time for Thursdays', default=datetime.time(hour=8, minute=0))
    thur_end = Column(DateTime(True), doc='End time for Thursdays', default=datetime.time(hour=16, minute=0))
    fri_start = Column(DateTime(True), doc='Start time for Fridays', default=datetime.time(hour=8, minute=0))
    fri_end = Column(DateTime(True), doc='End time for Fridays', default=datetime.time(hour=16, minute=0))
    sat_start = Column(DateTime(True), doc='Start time for Saturdays', default=datetime.time(hour=10, minute=0))
    sat_end = Column(DateTime(True), doc='End time for Saturdays', default=datetime.time(hour=14, minute=0))
