from sys import stderr

from flask import Blueprint
from flask import session
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import render_template

from flask_login import login_user
from flask_login import login_required
from flask_login import logout_user
from flask_login import current_user

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import MultipleResultsFound

from ..model import Permission
from ..model import User
from ..extensions import db, login_manager, auth_app_type

import os
import msal

auth = Blueprint('auth', __name__)

AUTHORITY = os.getenv('AAD_AUTHORITY', 'https://login.microsoftonline.com/common')
CLIENT_ID = os.getenv('AAD_CLIENT_ID')
CLIENT_SECRET = os.getenv('AAD_CLIENT_SECRET')
REDIRECT_PATH = os.getenv('AAD_REDIRECT_PATH')

@auth.route("/")
def index():
    session["flow"] = _build_auth_code_flow()
    return render_template('index.html', user=current_user, auth_url=session["flow"]["auth_uri"])

@auth.route(REDIRECT_PATH)
def authorized():
    """
    Called when a user has authenticated with their microsoft account.
    We save their user info as a server side session. Any routes that
    require authentication can check if this user exists.
    """
    try:
        cache = _load_cache()
        msal_app = _build_auth_app(cache=cache)
        result = msal_app.acquire_token_by_auth_code_flow(session.get("flow", {}), request.args)

        if "error" in result:
            return render_template("auth_error.html", result=result)

        claims = result.get("id_token_claims")
        login_user(_user_from_claims(claims))
        _save_cache(cache)

    except ValueError:  # Usually caused by CSRF, Simply ignore them
        pass

    except Exception as e:
        flash('Could not sign-in, unknown error.', category='error')
        print(f'{e}', file=stderr)

    return redirect(url_for("auth.index"))

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(f'{AUTHORITY}/oauth2/v2.0/logout?post_logout_redirect_uri={url_for("auth.index", _external=True)}')

@login_manager.unauthorized_handler
def unauthorized():
    session["flow"] = _build_auth_code_flow()
    return redirect(session["flow"]["auth_uri"])

@login_manager.user_loader
def user_loader(id: str):
    # TODO: flask-login provides the primary key of the user object
    #       which is currently just an auto increment integer.
    #       However, we may consider using the OID as a key instead
    #       in which case this function should just call _user_from_claims
    #
    return User.query.get(int(id))

def _user_from_claims(token_claims: str):
    """
    Load or create a user object from the database given auth token claims.
    Returns the User object or None if more than one user with the same OID is found.
    """
    oid = token_claims.get('oid')

    try:
        user: User = User.query.filter_by(oid=oid).one_or_none()

    except MultipleResultsFound as e:
        e.add_note(f'Found more than one user for oid: \'{oid}\'')
        raise e

    # This may be an incomplete user
    if user is None:
        name = token_claims.get('name')
        preferred_name = token_claims.get('preferred_username')

        try:
            user: User = User.query.filter_by(email=preferred_name).one_or_none()

        except MultipleResultsFound as e:
            e.add_note(f'Found more than one user for email: \'{preferred_name}\'')
            raise e

        # If user was found by email complete the remaining info
        if user:
            user.oid = oid
            user.name = name
            print(f'User was completed: {user}')

        # If User still not found, then they don't exist in database, create new entry
        else:
            print(f'Creating new entry in database for user {oid}...')
            user = User(oid, Permission.Student, preferred_name, name, False, False)

        try:
            db.session.add(user)
            db.session.commit()

        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    # TODO: Check if user is active tutor/admin and set them as actively working

    return user

def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])

    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def _build_auth_app(cache=None):
    assert CLIENT_ID, 'No client ID specified for authentication. Set AAD_CLIENT_ID env variable!'
    assert CLIENT_SECRET, 'No client secret specified for authentication. Set AAD_CLIENT_SECRET env variable!'
    assert REDIRECT_PATH, 'No redirect path specified for authentication. Set AAD_REDIRECT_PATH env variable!'
    return auth_app_type(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET, token_cache=cache)

def _build_auth_code_flow(scopes=None):
    return _build_auth_app().initiate_auth_code_flow(scopes or [], redirect_uri=url_for("auth.authorized", _external=True))
