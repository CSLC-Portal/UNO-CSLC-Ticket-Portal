
from functools import wraps

from flask import flash
from flask import redirect
from flask import url_for

from flask_login import login_required
from flask_login import current_user

from .model import Permission

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

            # Permission is effectively Permission.Student if user is not active
            effective_permission = current_user.permission if current_user.tutor_is_active else Permission.Student

            if effective_permission < permission:
                flash('Insufficient privileges to access this page!', category='error')
                return redirect(url_for(PERMISSION_REQUIRED_REDIRECT))

            return func(*args, **kwargs)
        return wrapper
    return decorator
