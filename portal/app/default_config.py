
from .extensions import db
import datetime
import os

# NOTE: This file contains default configurations for flask, it does not need to be changed.
#       if you wish to override any of these settings set the corresponding environment variables
#       (prefixed with 'FLASK_').

# Encrypt cookies, generate a random cryotographically-secure string
SECRET_KEY = os.urandom(512)

# Session cookies will only be valid for 30 minutes of inactivity
PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=30)

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# Flask-SQLAlchemy default options
# Some database management systems break connection after some time of inactivity (e.g. MySQL)
# Refresh the connection frequently to circumvent this.
SQLALCHEMY_ENGINE_OPTIONS = { 'pool_recycle': 3600 }

# Default data base is sqlite, this is overriden in production
SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'

# Flask-Session default options
# Specifies the token cache should be stored in server-side session
SESSION_TYPE = 'sqlalchemy'

# We set the db for Flask-Session here, before the tables are created
SESSION_SQLALCHEMY = db
