
import datetime
import os

# Encrypt cookies, generate a random cryotographically-secure string
SECRET_KEY = os.urandom(512)

# Session cookies will only be valid for 30 minutes of inactivity
PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=30)

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
