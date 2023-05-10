
from flask import Flask
from flask.testing import FlaskClient

from app.model import ProblemType

def test_admin_remove_problem_type(admin_client: FlaskClient, app: Flask):
    response = admin_client.post('/admin/problems/remove', data={ 'problemTypeID': '1' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/problems"' in response.data

    with app.app_context():
        assert ProblemType.query.count() == 1

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'Problem type successfully removed!'

def test_admin_remove_problem_type_no_data(admin_client: FlaskClient, app: Flask):
    response = admin_client.post('/admin/problems/remove')

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
        assert message == 'Could not delete problem type, problem type does not exist!'

def test_admin_remove_problem_type_invalid_data(admin_client: FlaskClient, app: Flask):
    response = admin_client.post('/admin/problems/remove', data={ 'problemType': '' })

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
        assert message == 'Could not delete problem type, problem type does not exist!'
