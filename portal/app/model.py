from sqlalchemy import Column, String, Integer, DateTime, Enum, Boolean, Time
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from .extensions import db
from flask_login import UserMixin
import enum

Base = declarative_base(name='Base')

class Status(enum.Enum):
    """
    This Status class is designed to mimic an enum for values of which a ticket can obtain for its status value.
    A ticket can have the following three status values: Open, Claimed, or Closed. As shown below as well.
    """
    Open = 1
    Claimed = 2
    Closed = 3

class Mode(enum.Enum):
    """
    Mode class is designed to mimic an enum for values of which a ticket can be submitted.
    A ticket can either be submitted for online or inperson help. As shown below.
    """
    Online = 1
    InPerson = 2

class Ticket(db.Model):
    """
    The Ticket class is the main Model for the ticket objects that get created when students create and submit thier tickets for help.
    Every time a ticket is created, the student will only actualy enter in the following information:
    student_email, student_name, course, seciton, assignment_name, specific_question, and problem_type.
    The rest of the data fields are used in backoffice processing.
    """
    __tablename__ = 'Tickets'

    id = Column(Integer, primary_key=True, doc='Autonumber primary key for the ticket table.')
    student_email = Column(String(25), nullable=False, doc='Email of the student making the ticket.')
    student_name = Column(String(25), doc='The name of student making the ticket.')
    course = Column(String(25), doc='The specific course this ticket issue is related to.')
    section = Column(String(25), doc='Course section ticket issue is relating to.')
    assignment_name = Column(String(25), doc='Assignment the student needs help with.')
    specific_question = Column(String(25), doc='Student question about the assignment.')
    problem_type = Column(String(25), doc='Type of problem the student is having.')
    time_created = Column(DateTime(True), nullable=False, doc='Time the ticket was created.', default=func.now())
    time_claimed = Column(DateTime(True), doc='Time the ticket was claimed by tutor.')
    status = Column(Enum(Status), doc='Status of the ticket. 1=open, 2=claimed, 3=closed.', default=Status.Open)
    time_closed = Column(DateTime(True), doc='Time the tutor marked the ticket as closed.')
    session_duration = Column(Time(True), doc='Amount of time the tutor spent on the ticket/student.')
    mode = Column(Enum(Mode), doc='Specifies whether the ticket was made for online or in-person help.')
    tutor_notes = Column(String(255), doc='Space for tutors to write notes about student/ticket session.', default="")
    tutor_id = Column(Integer, db.ForeignKey('Users.id'), doc='Foreign key to the tutor who claimed this ticket.')
    successful_session = Column(Boolean, doc='T/F if the tutor was able to help the student with issue on ticket')

    def __init__(self, sEmailIn, sNameIn, crsIn, secIn, assgnIn, quesIn, prblmIn, modeIn):
        self.student_email = sEmailIn
        self.student_name = sNameIn
        self.course = crsIn
        self.section = secIn
        self.assignment_name = assgnIn
        self.specific_question = quesIn
        self.problem_type = prblmIn
        self.mode = modeIn

class User(db.Model, UserMixin):
    """
    The User class is the main model for every user that interacts with the CSLC Portal. In general there are only
    three types ofusers: students, tutuors, and admins. In order to determine what user is what, we have added a field
    called 'permission_level' which specifies which type of user the user object is. For example, a student User would have
    permission level of 1, tutor a permission level of 2, and an admin a permission level of 3. This way we can restrict what certain
    users are able to do on the CSLC portal like adding/modifying tutors, viewing ticket data, generating reports, etc
    """
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True, doc='Autonumber primary key')
    oid = Column(String(50), doc='ID token returned for the requestor')
    permission_level = Column(Integer(), nullable=False, doc='Specifies permission level of user. e.g. 0=lowest, 3=superuser')
    user_email = Column(String(25), nullable=False, doc='Email of user')
    user_name = Column(String(25), doc='Users name')
    tutor_is_active = Column(Boolean, doc='T/F if the tutor is currently employed')
    tutor_is_working = Column(Boolean, doc='T/F if the tutor is currently working')
    tickets = db.relationship('Ticket', backref='user')
    # TODO: below are items that will eventually need to be defined as relationships to other tables that aren't yet created
    #  - assisted_tickets
    #  - courses

    def __init__(self, oidIn, permLevelIn, emailIn, nameIn, isActiveIn, isWorkingIn):
        self.oid = oidIn
        self.permission_level = permLevelIn
        self.user_email = emailIn
        self.user_name = nameIn
        self.tutor_is_active = isActiveIn
        self.tutor_is_working = isWorkingIn

    def __repr__(self):
        return f'{self.user_name} ({self.user_email})'
