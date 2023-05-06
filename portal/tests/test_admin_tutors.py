
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Query

from app.model import Permission
from app.model import User

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
        pending: Query = User.get_pending()

        assert pending.count() == 1

        user: User = pending.first()
        assert not user.is_complete()
        assert user.email == 'new@user.com'
        assert user.permission == Permission.Admin
        assert user.tutor_is_active

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'New user successfully added!'

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
        assert user.tutor_is_active

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'New user successfully added!'

def test_admin_add_admin_existing_user(admin_client: FlaskClient, create_auth_client, app: Flask):
    # Create another dummy user
    new_client_email = 'new@user.com'
    create_auth_client(name='same', email=new_client_email, oid='xxxx')

    with app.app_context():
        val = list(User.query.all())
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
        assert user.tutor_is_active

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'New user successfully added!'

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
        assert category == 'success'
        assert message == 'User successfully removed!'

    with app.app_context():
        assert User.get_tutors().count() == 1
        assert User.query.count() == 2
        assert not User.get_students().first().tutor_is_active

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

def test_admin_remove_pending_admin(admin_client: FlaskClient, app: Flask):
    response = admin_client.post('/admin/tutors/add', data={ 'email': 'new@user.com', 'permission': Permission.Admin.value })

    with app.app_context():
        assert User.get_tutors().count() == 1
        assert User.query.count() == 2

        pending: User = User.query.filter_by(email='new@user.com').one()
        assert not pending.is_complete()
        assert pending.permission == Permission.Admin

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
        assert message == 'Could not add user, invalid data'

def test_admin_add_invalid_email(admin_client: FlaskClient, app: Flask):
    # Empty email string
    response = admin_client.post('/admin/tutors/add', data={ 'email': '', 'permission': Permission.Admin.value })

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
        assert message == 'Could not add user, unknown reason'

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

