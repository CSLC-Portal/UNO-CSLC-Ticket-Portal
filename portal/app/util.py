
from functools import wraps

from flask import flash
from flask import redirect
from flask import url_for

from flask_login import login_required
from flask_login import current_user

PERMISSION_REQUIRED_REDIRECT = 'views.index'

def strip_or_none(s: str):
    return s.strip() if s is not None else None

def str_empty(s: str):
    return s is not None and not s

def permission_required(permission):
    def decorator(func):
        @wraps(func)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.permission < permission:
                flash('Insufficient privileges to access this page!', category='error')
                return redirect(url_for(PERMISSION_REQUIRED_REDIRECT))

            return func(*args, **kwargs)
        return wrapper
    return decorator

def build_days_of_week_string(mon, tue, wed, thu, fri):
    daysOfWeek = ""
    if mon is not None:
        daysOfWeek = daysOfWeek + "Mon"
    if tue is not None:
        daysOfWeek = daysOfWeek + "Tue"
    if wed is not None:
        daysOfWeek = daysOfWeek + "Wed"
    if thu is not None:
        daysOfWeek = daysOfWeek + "Thu"
    if fri is not None:
        daysOfWeek = daysOfWeek + "Fri"

    return daysOfWeek
