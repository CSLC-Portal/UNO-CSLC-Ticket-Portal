from flask import Blueprint
from flask import request
from flask import flash
from flask import url_for
from flask import redirect
from flask import render_template

from app.model import ProblemTypes
from app.extensions import db

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
