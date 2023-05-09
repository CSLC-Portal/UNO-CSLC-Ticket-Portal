
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Query

from app.model import Permission
from app.model import User
from app.extensions import db

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

def test_admin(admin_client: FlaskClient, admin_urls):
    for url in admin_urls:
        if 'GET' not in url.methods:
            continue

        response = admin_client.get(url.rule)

        # Expect redirect back to index
        assert '200' in response.status
        assert b'Admin Console' in response.data

def test_owner(owner_client: FlaskClient, admin_urls):
    for url in admin_urls:
        if 'GET' not in url.methods:
            continue

        response = owner_client.get(url.rule)

        # Expect redirect back to index
        assert '200' in response.status
        assert b'Admin Console' in response.data

# Add user tests

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
        assert user.tutor_is_active

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'New user successfully added!'

def test_admin_add_admin(admin_client: FlaskClient, app: Flask):
    response = admin_client.post('/admin/tutors/add', data={ 'email': 'new@user.com', 'permission': Permission.Admin.value })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with app.app_context():
        assert User.get_tutors().count() == 1

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Cannot add user of higher or equal permission level as yourself!'

def test_admin_add_owner(admin_client: FlaskClient, app: Flask):
    response = admin_client.post('/admin/tutors/add', data={ 'email': 'new@user.com', 'permission': Permission.Owner.value })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with app.app_context():
        assert User.get_tutors().count() == 1

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Cannot add user of higher or equal permission level as yourself!'

def test_owner_add_tutor(owner_client: FlaskClient, app: Flask):
    response = owner_client.post('/admin/tutors/add', data={ 'email': 'new@user.com', 'permission': Permission.Tutor.value })

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
        assert user.tutor_is_active

    with owner_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'New user successfully added!'

def test_owner_add_admin(owner_client: FlaskClient, app: Flask):
    response = owner_client.post('/admin/tutors/add', data={ 'email': 'new@user.com', 'permission': Permission.Admin.value })

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
        assert user.tutor_is_active

    with owner_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'New user successfully added!'

def test_owner_add_owner(admin_client: FlaskClient, app: Flask):
    response = admin_client.post('/admin/tutors/add', data={ 'email': 'new@user.com', 'permission': Permission.Owner.value })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with app.app_context():
        assert User.get_tutors().count() == 1

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Cannot add user of higher or equal permission level as yourself!'

def test_admin_add_self(create_super_user, app: Flask):
    admin_email = 'admin@email.com'
    admin_client = create_super_user(email=admin_email)

    with app.app_context():
        assert User.get_tutors().count() == 1

    response = admin_client.post('/admin/tutors/add', data={ 'email': admin_email, 'permission': Permission.Tutor.value })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'User already exists in the role hierarchy!'


    with app.app_context():
        assert User.get_tutors().count() == 1
        assert User.query.count() == 1

def test_admin_add_existing_user(admin_client: FlaskClient, create_auth_client, app: Flask):
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
        assert user.tutor_is_active

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'New user successfully added!'

def test_admin_add_existing_super_user(admin_client: FlaskClient, create_super_user, app: Flask):
    new_client_email = 'some@email.com'
    create_super_user(email=new_client_email, oid='xxxx')

    with app.app_context():
        assert User.get_tutors().count() == 2

    response = admin_client.post('/admin/tutors/add', data={ 'email': new_client_email, 'permission': Permission.Tutor.value })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'User already exists in the role hierarchy!'

    with app.app_context():
        assert User.get_tutors().count() == 2

def test_admin_add_no_data(admin_client: FlaskClient, app: Flask):
    response = admin_client.post('/admin/tutors/add')

    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with app.app_context():
        assert User.get_pending().count() == 0
        assert User.query.count() == 1

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not add user, invalid data!'

def test_admin_add_invalid_email(admin_client: FlaskClient, app: Flask):
    # Empty email string
    response = admin_client.post('/admin/tutors/add', data={ 'email': '', 'permission': Permission.Tutor.value })

    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with app.app_context():
        assert User.get_pending().count() == 0
        assert User.query.count() == 1

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Email must not be empty!'

def test_admin_add_invalid_permission(admin_client: FlaskClient, app: Flask):
    # Invalid permission value
    response = admin_client.post('/admin/tutors/add', data={ 'email': '', 'permission': 69 })

    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with app.app_context():
        assert User.get_pending().count() == 0
        assert User.query.count() == 1

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not add user, must select a valid mode!'

# Remove tutor tests

def test_admin_remove_tutor(admin_client: FlaskClient, create_super_user, app: Flask):
    create_super_user(email='tutor@email.com', oid='xxxx', permission = Permission.Tutor)

    with app.app_context():
        assert User.get_tutors().count() == 2

    response = admin_client.post('/admin/tutors/remove', data={ 'userID': '2' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'User successfully removed!'

    with app.app_context():
        assert User.get_tutors().count() == 1
        assert User.query.count() == 2
        assert not User.get_students().first().tutor_is_active

def test_admin_remove_admin(admin_client: FlaskClient, create_super_user, app: Flask):
    create_super_user(email='admin2@email.com', oid='xxxx')

    with app.app_context():
        assert User.get_tutors().count() == 2

    response = admin_client.post('/admin/tutors/remove', data={ 'userID': '2' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Cannot remove user of higher or equal permission level as yourself!'

    with app.app_context():
        assert User.get_tutors().count() == 2

def test_admin_remove_owner(admin_client: FlaskClient, create_super_user, app: Flask):
    create_super_user(email='owner@email.com', oid='xxxx', permission=Permission.Owner)

    with app.app_context():
        assert User.get_tutors().count() == 2

    response = admin_client.post('/admin/tutors/remove', data={ 'userID': '2' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Cannot remove user of higher or equal permission level as yourself!'

    with app.app_context():
        assert User.get_tutors().count() == 2

def test_owner_remove_tutor(owner_client: FlaskClient, create_super_user, app: Flask):
    create_super_user(email='tutor@email.com', oid='xxxx', permission = Permission.Tutor)

    with app.app_context():
        assert User.get_tutors().count() == 2

    response = owner_client.post('/admin/tutors/remove', data={ 'userID': '2' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with owner_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'User successfully removed!'

    with app.app_context():
        assert User.get_tutors().count() == 1
        assert User.query.count() == 2
        assert not User.get_students().first().tutor_is_active

def test_owner_remove_admin(owner_client: FlaskClient, create_super_user, app: Flask):
    create_super_user(email='tutor@email.com', oid='xxxx')

    with app.app_context():
        assert User.get_tutors().count() == 2

    response = owner_client.post('/admin/tutors/remove', data={ 'userID': '2' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with owner_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'User successfully removed!'

    with app.app_context():
        assert User.get_tutors().count() == 1
        assert User.query.count() == 2
        assert not User.get_students().first().tutor_is_active

def test_owner_remove_owner(owner_client: FlaskClient, create_super_user, app: Flask):
    create_super_user(email='owner2@email.com', oid='xxxx', permission=Permission.Owner)

    with app.app_context():
        assert User.get_tutors().count() == 2

    response = owner_client.post('/admin/tutors/remove', data={ 'userID': '2' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with owner_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Cannot remove user of higher or equal permission level as yourself!'

    with app.app_context():
        assert User.get_tutors().count() == 2

def test_admin_remove_self(admin_client: FlaskClient, app: Flask):
    with app.app_context():
        assert User.get_tutors().count() == 1

    response = admin_client.post('/admin/tutors/remove', data={ 'userID': '1' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'You cannot remove yourself from the role hierarchy!'

    with app.app_context():
        assert User.get_tutors().count() == 1
        assert User.query.count() == 1

def test_admin_remove_pending_tutor(admin_client: FlaskClient, app: Flask):
    response = admin_client.post('/admin/tutors/add', data={ 'email': 'new@user.com', 'permission': Permission.Tutor.value })

    with app.app_context():
        assert User.get_tutors().count() == 1
        assert User.query.count() == 2

        pending: User = User.query.filter_by(email='new@user.com').one()
        assert not pending.is_complete()
        assert pending.permission == Permission.Tutor

    response = admin_client.post('/admin/tutors/remove', data={ 'userID': '2' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 2

        (category, message) = flashes[1]
        assert category == 'success'
        assert message == 'User successfully removed!'

    with app.app_context():
        assert User.get_tutors().count() == 1
        assert User.query.count() == 1

def test_admin_remove_no_data(admin_client: FlaskClient, create_super_user, app: Flask):
    response = admin_client.post('/admin/tutors/remove')

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not remove user, user does not exist!'

    with app.app_context():
        assert User.get_tutors().count() == 1

def test_admin_remove_invalid_id(admin_client: FlaskClient, create_super_user, app: Flask):
    response = admin_client.post('/admin/tutors/remove', data={ 'userID': '69' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not remove user, user does not exist!'

    with app.app_context():
        assert User.get_tutors().count() == 1

# Edit tutor tests

def test_admin_edit_tutor_to_admin(admin_client: FlaskClient, create_super_user, app: Flask):
    create_super_user(email='tutor@email.com', oid='xxxx', permission = Permission.Tutor)

    with app.app_context():
        user: User = User.query.filter_by(email='tutor@email.com').one()
        assert user.permission == Permission.Tutor

    response = admin_client.post('/admin/tutors/edit', data={'userID': '2', 'permission': Permission.Admin.value })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Cannot promote user to higher or equal permission level as yourself!'

    with app.app_context():
        user: User = User.query.filter_by(email='tutor@email.com').one()
        assert user.permission == Permission.Tutor

def test_admin_edit_tutor_to_owner(admin_client: FlaskClient, create_super_user, app: Flask):
    create_super_user(email='tutor@email.com', oid='xxxx', permission = Permission.Tutor)

    with app.app_context():
        user: User = User.query.filter_by(email='tutor@email.com').one()
        assert user.permission == Permission.Tutor

    response = admin_client.post('/admin/tutors/edit', data={'userID': '2', 'permission': Permission.Owner.value })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Cannot promote user to higher or equal permission level as yourself!'

    with app.app_context():
        user: User = User.query.filter_by(email='tutor@email.com').one()
        assert user.permission == Permission.Tutor

def test_owner_edit_tutor_to_admin(owner_client: FlaskClient, create_super_user, app: Flask):
    create_super_user(email='tutor@email.com', oid='xxxx', permission = Permission.Tutor)

    with app.app_context():
        user: User = User.query.filter_by(email='tutor@email.com').one()
        assert user.permission == Permission.Tutor

    response = owner_client.post('/admin/tutors/edit', data={'userID': '2', 'permission': Permission.Admin.value })

    with app.app_context():
        assert User.get_tutors().count() == 2

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with owner_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'User successfully updated!'

    with app.app_context():
        user: User = User.query.filter_by(email='tutor@email.com').one()
        assert user.permission == Permission.Admin

def test_owner_edit_tutor_to_owner(owner_client: FlaskClient, create_super_user, app: Flask):
    create_super_user(email='tutor@email.com', oid='xxxx', permission = Permission.Tutor)

    with app.app_context():
        user: User = User.query.filter_by(email='tutor@email.com').one()
        assert user.permission == Permission.Tutor

    response = owner_client.post('/admin/tutors/edit', data={'userID': '2', 'permission': Permission.Owner.value })

    with app.app_context():
        assert User.get_tutors().count() == 2

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with owner_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Cannot promote user to higher or equal permission level as yourself!'

    with app.app_context():
        user: User = User.query.filter_by(email='tutor@email.com').one()
        assert user.permission == Permission.Tutor

def test_admin_edit_tutor_to_inactive(admin_client: FlaskClient, create_super_user, app: Flask):
    create_super_user(email='tutor@email.com', oid='xxxx', permission = Permission.Tutor)

    with app.app_context():
        user: User = User.query.filter_by(email='tutor@email.com').one()
        assert user.tutor_is_active

    response = admin_client.post('/admin/tutors/edit', data={'userID': '2' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'User successfully updated!'

    with app.app_context():
        user: User = User.query.filter_by(email='tutor@email.com').one()
        assert not user.tutor_is_active

def test_admin_edit_admin_to_inactive(admin_client: FlaskClient, create_super_user, app: Flask):
    create_super_user(email='admin2@email.com', oid='xxxx', permission = Permission.Admin)

    with app.app_context():
        user: User = User.query.filter_by(email='admin2@email.com').one()
        assert user.tutor_is_active

    response = admin_client.post('/admin/tutors/edit', data={'userID': '2' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Cannot update user of higher or equal permission level as yourself!'

    with app.app_context():
        user: User = User.query.filter_by(email='admin2@email.com').one()
        assert user.tutor_is_active

def test_admin_edit_admin_to_inactive(admin_client: FlaskClient, create_super_user, app: Flask):
    create_super_user(email='owner@email.com', oid='xxxx', permission = Permission.Owner)

    with app.app_context():
        user: User = User.query.filter_by(email='owner@email.com').one()
        assert user.tutor_is_active

    response = admin_client.post('/admin/tutors/edit', data={'userID': '2' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Cannot update user of higher or equal permission level as yourself!'

    with app.app_context():
        user: User = User.query.filter_by(email='owner@email.com').one()
        assert user.tutor_is_active

def test_owner_edit_tutor_to_inactive(owner_client: FlaskClient, create_super_user, app: Flask):
    create_super_user(email='tutor@email.com', oid='xxxx', permission = Permission.Tutor)

    with app.app_context():
        user: User = User.query.filter_by(email='tutor@email.com').one()
        assert user.tutor_is_active

    response = owner_client.post('/admin/tutors/edit', data={'userID': '2' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with owner_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'User successfully updated!'

    with app.app_context():
        user: User = User.query.filter_by(email='tutor@email.com').one()
        assert not user.tutor_is_active

def test_owner_edit_admin_to_inactive(owner_client: FlaskClient, create_super_user, app: Flask):
    create_super_user(email='admin@email.com', oid='xxxx', permission = Permission.Admin)

    with app.app_context():
        user: User = User.query.filter_by(email='admin@email.com').one()
        assert user.tutor_is_active

    response = owner_client.post('/admin/tutors/edit', data={'userID': '2' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with owner_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'User successfully updated!'

    with app.app_context():
        user: User = User.query.filter_by(email='admin@email.com').one()
        assert not user.tutor_is_active

def test_owner_edit_owner_to_inactive(owner_client: FlaskClient, create_super_user, app: Flask):
    create_super_user(email='owner2@email.com', oid='xxxx', permission = Permission.Owner)

    with app.app_context():
        user: User = User.query.filter_by(email='owner2@email.com').one()
        assert user.tutor_is_active

    response = owner_client.post('/admin/tutors/edit', data={'userID': '2' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/tutors"' in response.data

    with owner_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Cannot update user of higher or equal permission level as yourself!'

    with app.app_context():
        user: User = User.query.filter_by(email='owner2@email.com').one()
        assert user.tutor_is_active

# Inactive logins

def test_tutor_inactive(create_super_user, app: Flask):
    tutor_client = create_super_user(email='tutor@email.com', permission = Permission.Tutor)

    with app.app_context():
        user: User = User.query.filter_by(email='tutor@email.com').one()
        user.tutor_is_active = False
        db.session.commit()

    response = tutor_client.get('/view-tickets')

    # Expect redirect back to index page
    assert '302' in response.status
    assert b'href="/"' in response.data

    with tutor_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Insufficient privileges to access this page!'

def test_admin_inactive(create_super_user, app: Flask):
    admin_client = create_super_user(email='admin@email.com', permission = Permission.Admin)

    with app.app_context():
        user: User = User.query.filter_by(email='admin@email.com').one()
        user.tutor_is_active = False
        db.session.commit()

    response = admin_client.get('/view-tickets')

    # Expect redirect back to index page
    assert '302' in response.status
    assert b'href="/"' in response.data

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Insufficient privileges to access this page!'
        session.clear()

def test_admin_inactive_admin(create_super_user, admin_urls, app: Flask):
    admin_client = create_super_user(email='admin@email.com', permission = Permission.Admin)

    with app.app_context():
        user: User = User.query.filter_by(email='admin@email.com').one()
        user.tutor_is_active = False
        db.session.commit()

    for url in admin_urls:
        if 'GET' not in url.methods:
            continue

        response = admin_client.get(url.rule)

        # Expect redirect back to index
        assert '302' in response.status
        assert b'href="/"' in response.data

        with admin_client.session_transaction() as session:
            flashes = session['_flashes']
            assert len(flashes) == 1

            (category, message) = flashes[0]
            assert category == 'error'
            assert message == 'Insufficient privileges to access this page!'
            session['_flashes'].clear()