from flask import Blueprint
from flask import render_template, session, request, redirect, url_for

import os
import msal

auth = Blueprint('auth', __name__)

AUTHORITY = os.getenv('AAD_AUTHORITY', 'https://login.microsoftonline.com/common')
CLIENT_ID = os.getenv('AAD_CLIENT_ID', 'NO-ID')
CLIENT_SECRET = os.getenv('AAD_CLIENT_SECRET', 'NO_SECRET')
REDIRECT_PATH = os.getenv('AAD_REDIRECT_PATH', '/getAToken')

@auth.route("/login")
def login():
    session["flow"] = _build_auth_code_flow()
    return render_template("login.html", auth_url=session["flow"]["auth_uri"])

@auth.route(REDIRECT_PATH)
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)

        if "error" in result:
            return render_template("auth_error.html", result=result)

        session["user"] = result.get("id_token_claims")
        _save_cache(cache)

    except ValueError: # Usually caused by CSRF, Simply ignore them
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
        authority = AUTHORITY,
        client_credential = CLIENT_SECRET,
        token_cache = cache)

def _build_auth_code_flow(scopes=None):
    return _build_msal_app().initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("auth.authorized", _external=True))
