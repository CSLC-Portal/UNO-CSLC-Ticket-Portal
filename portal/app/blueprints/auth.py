from flask import Blueprint
from flask import render_template, session, request, redirect, url_for

import os
import msal

auth = Blueprint('auth', __name__)

AUTHORITY = os.getenv('AAD_AUTHORITY', 'https://login.microsoftonline.com/common')
CLIENT_ID = os.getenv('AAD_CLIENT_ID')
CLIENT_SECRET = os.getenv('AAD_CLIENT_SECRET')
REDIRECT_PATH = os.getenv('AAD_REDIRECT_PATH')

assert CLIENT_ID, 'No client ID specified for authentication. Set AAD_CLIENT_ID env variable!'
assert CLIENT_SECRET, 'No client secret specified for authentication. Set AAD_CLIENT_SECRET env variable!'
assert REDIRECT_PATH, 'No redirect path specified for authentication. Set AAD_REDIRECT_PATH env variable!'

@auth.route("/login")
def login():
    session["flow"] = _build_auth_code_flow()
    return render_template("login.html", auth_url=session["flow"]["auth_uri"])

@auth.route(REDIRECT_PATH)
def authorized():
    """
    Called when a user has authenticated with their microsoft account.
    We save their user info as a server side session. Any routes that
    require authentication can check if this user exists.
    """
    try:
        cache = _load_cache()
        msal_app = _build_msal_app(cache=cache)
        result = msal_app.acquire_token_by_auth_code_flow(session.get("flow", {}), request.args)

        if "error" in result:
            return render_template("auth_error.html", result=result)

        session["user"] = result.get("id_token_claims")
        _save_cache(cache)

    except ValueError:  # Usually caused by CSRF, Simply ignore them
        pass

    return redirect(url_for("views.index"))

@auth.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(f'{AUTHORITY}/oauth2/v2.0/logout?post_logout_redirect_uri={url_for("views.index", _external=True)}')

def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])

    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def _build_msal_app(cache=None):
    return msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
        token_cache=cache)

def _build_auth_code_flow(scopes=None):
    return _build_msal_app().initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("auth.authorized", _external=True))
