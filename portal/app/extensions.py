
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

db = SQLAlchemy()

# Create server-side session for sensitive information
sess = Session()
