
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_login import LoginManager

db = SQLAlchemy()

# Create server-side session for sensitive information
sess = Session()

# Login manager will use server-side sessions automatically
login_manager = LoginManager()
