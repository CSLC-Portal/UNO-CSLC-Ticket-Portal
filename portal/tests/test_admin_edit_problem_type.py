
from flask import Flask
from flask.testing import FlaskClient

from app.model import ProblemType

def test_admin_edit_problem_type(admin_client: FlaskClient, app: Flask):
    response = admin_client.post('/admin/problems/edit', data={ 'problemTypeID': '1', 'description': 'New description!' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/problems"' in response.data

    with app.app_context():
        assert ProblemType.query.count() == 2

        problemType: ProblemType = ProblemType.query.get('1')
        assert problemType.id == 1
        assert problemType.problem_type == 'New description!'

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'success'
        assert message == 'Problem type successfully updated!'

def test_admin_edit_problem_type_no_data(admin_client: FlaskClient, app: Flask):
    response = admin_client.post('/admin/problems/edit')

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/problems"' in response.data

    with app.app_context():
        assert ProblemType.query.count() == 2

        # Make sure we didn't change anything!
        for problem in ProblemType.query.all():
            assert problem.problem_type is not None

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not update problem type, problem type does not exist!'

def test_admin_edit_problem_type_invalid_id(admin_client: FlaskClient, app: Flask):
    response = admin_client.post('/admin/problems/edit', data={ 'problemTypeID': 'asd', 'description': 'blah blah blah' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/problems"' in response.data

    with app.app_context():
        assert ProblemType.query.count() == 2

        # Make sure we didn't change anything!
        for problem in ProblemType.query.all():
            assert problem.problem_type != 'blah blah blah'

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not update problem type, problem type does not exist!'

def test_admin_edit_problem_type_invalid_data(admin_client: FlaskClient, app: Flask):
    response = admin_client.post('/admin/problems/edit', data={ 'problemTypeID': '1', 'description': '' })

    # Expect redirect back to create ticket page
    assert '302' in response.status
    assert b'href="/admin/problems"' in response.data

    with app.app_context():
        assert ProblemType.query.count() == 2

        # Make sure we didn't change anything!
        for problem in ProblemType.query.all():
            assert problem.problem_type != ''

    with admin_client.session_transaction() as session:
        flashes = session['_flashes']
        assert len(flashes) == 1

        (category, message) = flashes[0]
        assert category == 'error'
        assert message == 'Could not update problem type, description must not be empty!'
