from flask import Flask

# NOTE: DO NOT change the name of 'app', it is used by gunicorn
app = Flask(__name__)

from app import views
