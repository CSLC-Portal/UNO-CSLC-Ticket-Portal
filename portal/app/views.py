from app import app
from flask import render_template

@app.route('/')
def index():
    return 'Future site of the CSLC Tutoring Portal!'

@app.route('/create-ticket')
def create_ticket():
    return render_template('create-ticket.html')
