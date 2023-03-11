from flask import Blueprint

views = Blueprint('views', __name__)

@views.route('/')
def index():
    return 'Future site of the CSLC Tutoring Portal!'
