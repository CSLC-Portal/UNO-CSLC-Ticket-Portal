from flask import Blueprint
from flask import request
from flask import flash
from flask import url_for
from flask import redirect
from flask import render_template

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/')
def console():
    return render_template('admin-console.html')
