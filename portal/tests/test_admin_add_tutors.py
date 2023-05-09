
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Query

from app.model import Permission
from app.model import User

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
