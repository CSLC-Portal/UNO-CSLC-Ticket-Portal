
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Query

from app.model import Permission
from app.model import User

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

def test_admin_remove_no_data(admin_client: FlaskClient, app: Flask):
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

def test_admin_remove_invalid_id(admin_client: FlaskClient, app: Flask):
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
