from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from .extensions import db

Base = declarative_base(name='Base')

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
