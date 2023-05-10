
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Query

from app.model import Permission
from app.model import User

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
