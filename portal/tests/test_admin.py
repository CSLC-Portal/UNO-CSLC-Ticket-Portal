
from flask import Flask
from flask.testing import FlaskClient

import pytest

@pytest.fixture
def admin_urls(app: Flask):
    return [ url for url in app.url_map.iter_rules() if app.blueprints['admin'].url_prefix in url.rule ]

def test_admin_unauthenticated(client: FlaskClient, admin_urls):
    for url in admin_urls:
        if 'GET' in url.methods:
            response = client.get(url.rule)

            # Expect redirect to sign-in
            assert '302' in response.status
            assert b'https://login.microsoftonline.com/common' in response.data

        if 'POST' in url.methods:
            response = client.post(url.rule)

            # Expect redirect to sign-in
            assert '302' in response.status
            assert b'https://login.microsoftonline.com/common' in response.data

def test_admin_insufficient_privileges_student(auth_client: FlaskClient, admin_urls):
    for url in admin_urls:
        if 'GET' in url.methods:
            response = auth_client.get(url.rule)

            # Expect redirect back to index
            assert '302' in response.status
            assert b'href="/"' in response.data

        if 'POST' in url.methods:
            response = auth_client.post(url.rule)

            # Expect redirect back to index
            assert '302' in response.status
            assert b'href="/"' in response.data

        with auth_client.session_transaction() as session:
            flashes = session['_flashes']
            assert len(flashes) >= 1

            (category, message) = flashes[0]
            assert category == 'error'
            assert message == 'Insufficient privileges to access this page!'

def test_admin_insufficient_privileges_tutor(tutor_client: FlaskClient, admin_urls):
    for url in admin_urls:
        if 'GET' in url.methods:
            response = tutor_client.get(url.rule)

            # Expect redirect back to index
            assert '302' in response.status
            assert b'href="/"' in response.data

        if 'POST' in url.methods:
            response = tutor_client.post(url.rule)

            # Expect redirect back to index
            assert '302' in response.status
            assert b'href="/"' in response.data

        with tutor_client.session_transaction() as session:
            flashes = session['_flashes']
            assert len(flashes) >= 1

            (category, message) = flashes[0]
            assert category == 'error'
            assert message == 'Insufficient privileges to access this page!'

def test_admin_sufficient_privileges(admin_client: FlaskClient, admin_urls):
    for url in admin_urls:
        if 'GET' not in url.methods:
            continue

        response = admin_client.get(url.rule)

        # Expect redirect back to index
        assert '200' in response.status
