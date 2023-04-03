from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, DateTime, Date, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from .extensions import db
import enum

Base = declarative_base(name='Base')

class Status (enum.Enum):
    #used to set the status of tickets
    Open = 1
    Claimed = 2
    Closed = 3

class Ticket(db.Model):
    __tablename__ = 'Tickets'

    id = Column(Integer, primary_key=True, doc='Autonumber primary key')
    student_email = Column(String(25), nullable=False, doc='Email of student making ticket')
    student_fname = Column(String(25), doc='First name of student makign ticket')
    student_lname = Column(String(25), doc='Last name of student making ticket')
    course = Column(String(25), doc='Course ticket issue is related to')
    section = Column(String(25), doc='Course section ticket issue is relating to')
    assignment_name = Column(String(25), doc='Assignment student needs help with')
    specific_question = Column(String(25), doc='Student question about the assignment')
    problem_type = Column(String(25), doc='Type of problem student is having')
    time_created = Column(DateTime(True), nullable=False, doc='Time ticket was created')
    status = Column(Enum(Status), doc='Status of the ticket. 1=open, 2=claimed, 3=closed')
    time_closed = Column(DateTime(True), doc='Time the tutor marked ticket as closed')
    session_duration = Column(Integer, doc='Amount of time the tutor spent on the ticket/student')
    #tutor_id = Column() This will be a foreign key to tutors table


    def __init__(self, sEmailIn, sFnameIn, sLnameIn, crsIn, secIn, assgnIn, quesIn, prblmIn, timeIn):
        self.student_email = sEmailIn
        self.student_fname = sFnameIn
        self.student_lname = sLnameIn
        self.course = crsIn
        self.section = secIn
        self.assignment_name = assgnIn
        self.specific_question = quesIn
        self.problem_type = prblmIn
        self.time_created = timeIn

class User(db.Model):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True, doc='Autonumber primary key')
    oid = Column(String(50), doc='ID token returned for the requestor')
    permission_level = Column(Integer(), nullable=False, doc='Specifies permission level of user. e.g. 0=lowest, 3=superuser')
    user_email = Column(String(25), nullable=False, doc='Email of user')
    user_fname = Column(String(25), doc='Users first name')
    user_lname = Column(String(25), doc='Users last name')
    tutor_is_active = Column(Boolean, doc='T/F if the tutor is currently employed')
    tutor_is_working = Column(Boolean, doc='T/F if the tutor is currently working')
    # below are items that will eventually need to be defined as relationships to other tables that aren't yet created
    # tickets
    # assisted_tickets
    # courses

    def __init__(self, oidIn, permLevelIn, emailIn, fnameIn, lnameIn, isActiveIn, isWorkingIn):
        self.oid = oidIn
        self.permission_level = permLevelIn
        self.user_email = emailIn
        self.user_fname = fnameIn
        self.user_lname = lnameIn
        self.tutor_is_active = isActiveIn
        self.tutor_is_working = isWorkingIn


