
from flask import Flask
from flask.testing import FlaskClient

from app.model import ProblemType

def test_admin_add_problem_type(admin_client: FlaskClient, app: Flask):
    response = admin_client.post('/admin/problems/add', data={ 'problemType': 'This is a problem!' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/problems"' in response.data

    with app.app_context():
        assert ProblemType.query.count() == 3

        problemType: ProblemType = ProblemType.query.filter_by(problem_type='This is a problem!').one()
        assert problemType.id == 3
        assert problemType.problem_type == 'This is a problem!'

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'Problem type created successfully!'

def test_admin_add_problem_type_no_data(admin_client: FlaskClient, app: Flask):
    response = admin_client.post('/admin/problems/add')

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/problems"' in response.data

    with app.app_context():
        assert ProblemType.query.count() == 2

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not create problem type, invalid data!'

def test_admin_add_problem_type_invalid_data(admin_client: FlaskClient, app: Flask):
    response = admin_client.post('/admin/problems/add', data={ 'problemType': '' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/problems"' in response.data

    with app.app_context():
        assert ProblemType.query.count() == 2

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not create problem type, description must not be empty!'
