from sys import stderr
from flask import Blueprint
from flask import render_template, session, request, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.orm import Query
from sqlalchemy.orm.exc import MultipleResultsFound

from datetime import datetime

from ..model import User, Messages, Config
from ..extensions import db, login_manager, auth_app_type

import os
import msal

auth = Blueprint('auth', __name__)

AUTHORITY = os.getenv('AAD_AUTHORITY', 'https://login.microsoftonline.com/common')
CLIENT_ID = os.getenv('AAD_CLIENT_ID')
CLIENT_SECRET = os.getenv('AAD_CLIENT_SECRET')
REDIRECT_PATH = os.getenv('AAD_REDIRECT_PATH')

def validate():
    assert CLIENT_ID, 'No client ID specified for authentication. Set AAD_CLIENT_ID env variable!'
    assert CLIENT_SECRET, 'No client secret specified for authentication. Set AAD_CLIENT_SECRET env variable!'
    assert REDIRECT_PATH, 'No redirect path specified for authentication. Set AAD_REDIRECT_PATH env variable!'

@auth.route("/")
def index():
    session["flow"] = _build_auth_code_flow()
    messages = Messages.query.filter(Messages.start_date < datetime.now(), Messages.end_date > datetime.now())
    config = Config.query.one()
    return render_template('index.html', user=current_user, auth_url=session["flow"]["auth_uri"], messages=messages, config=config)

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
        user: Query = User.query.filter_by(oid=oid).one_or_none()

    except MultipleResultsFound:
        print(f'Found more than one user for oid: \'{oid}\'', file=stderr)
        return

    # User does not exist in database, create new entry
    if user is None:
        print(f'Creating new entry in database for user {oid}...')
        name = token_claims.get('name')
        preferred_name = token_claims.get('preferred_username')
        user = User(oid, 0, preferred_name, name, False, False)

        db.session.add(user)
        db.session.commit()

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
    return auth_app_type(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET, token_cache=cache)

def _build_auth_code_flow(scopes=None):
    return _build_auth_app().initiate_auth_code_flow(scopes or [], redirect_uri=url_for("auth.authorized", _external=True))
