
# TODO: Make sure the flashed messages are correct!

import email
from flask import Flask, ctx
from flask.testing import FlaskClient
from sqlalchemy.orm import Query

from app.model import Permission
from app.model import User

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

def test_admin(admin_client: FlaskClient, admin_urls):
    for url in admin_urls:
        if 'GET' not in url.methods:
            continue

        response = admin_client.get(url.rule)

        # Expect redirect back to index
        assert '200' in response.status
        assert b'Admin Console' in response.data

def test_admin_add_tutor(admin_client: FlaskClient, app: Flask):
    response = admin_client.post('/admin/tutors/add', data={ 'email': 'new@user.com', 'permission': Permission.Tutor.value })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with app.app_context():
        pending: Query = User.get_pending()

        assert pending.count() == 1

        user: User = pending.first()
        assert not user.is_complete()
        assert user.email == 'new@user.com'
        assert user.permission == Permission.Tutor

def test_admin_add_admin(admin_client: FlaskClient, app: Flask):
    response = admin_client.post('/admin/tutors/add', data={ 'email': 'new@user.com', 'permission': Permission.Admin.value })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with app.app_context():
        pending: Query = User.get_pending()

        assert pending.count() == 1

        user: User = pending.first()
        assert not user.is_complete()
        assert user.email == 'new@user.com'
        assert user.permission == Permission.Admin

def test_admin_add_tutor_existing_user(admin_client: FlaskClient, create_auth_client, app: Flask):
    # Create another dummy user
    new_client_email = 'new@user.com'
    create_auth_client(name='same', email=new_client_email, oid='xxxx')

    with app.app_context():
        assert User.query.count() == 2

    response = admin_client.post('/admin/tutors/add', data={ 'email': new_client_email, 'permission': Permission.Tutor.value })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with app.app_context():
        pending: Query = User.get_pending()

        assert pending.count() == 0

        user: User = User.query.filter_by(email = new_client_email).first()
        assert user.is_complete()
        assert user.email == 'new@user.com'
        assert user.permission == Permission.Tutor

def test_admin_add_admin_existing_user(admin_client: FlaskClient, create_auth_client, app: Flask):
    # Create another dummy user
    new_client_email = 'new@user.com'
    create_auth_client(name='same', email=new_client_email, oid='xxxx')

    with app.app_context():
        assert User.query.count() == 2

    response = admin_client.post('/admin/tutors/add', data={ 'email': new_client_email, 'permission': Permission.Admin.value })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with app.app_context():
        pending: Query = User.get_pending()

        assert pending.count() == 0

        user: User = User.query.filter_by(email = new_client_email).first()
        assert user.is_complete()
        assert user.email == 'new@user.com'
        assert user.permission == Permission.Admin
