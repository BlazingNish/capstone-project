import pytest
from app import create_app
from app.models import User, db


@pytest.fixture
def client():
    # Create a test Flask app
    app = create_app()
    app.config['TESTING'] = True
    # Use an in-memory SQLite database for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing

    # Create a test client
    with app.test_client() as client:
        # Push an application context
        with app.app_context():
            db.create_all()  # Create the database tables
        yield client  # Provide the client to the tests

        # Tear down the database after the test
        with app.app_context():
            db.session.remove()  # Ensure the session is closed
            db.drop_all()
@pytest.fixture
def auth_token():
    return "admin"

def testCreatUser(client):
    response = client.post(
        '/users', json={'username': 'test', 'email': 'test@example.com'})
    assert response.status_code == 201
    assert response.json["message"] == "User created"


def testGetUsers(client, auth_token):
    client.post(
        '/users', json={'username': 'test', 'email': 'test@example.com'})
    response = client.get('/users', headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['username'] == 'test'
    assert response.json[0]['email'] == 'test@example.com'

def testGetUser(client, auth_token):
    with client.application.app_context():
        user = User(username="test_user", email="test@example.com")
        db.session.add(user)
        db.session.commit()
        response = client.get(f'/users/{user.id}', headers={'Authorization': f'Bearer {auth_token}'})
        assert response.status_code == 200
        assert response.json["username"] == "test_user"
        assert response.json["email"] == "test@example.com"

def testUpdateUser(client, auth_token):
    with client.application.app_context():
        user = User(username="test", email="test@example.com")
        db.session.add(user)
        db.session.commit()

        response = client.put(f'/users/{user.id}', json={'username': 'updatedTest', 'email': 'test@example.com'}, headers = {'Authorization': f'Bearer {auth_token}'})
        assert response.status_code == 200
        assert response.json['message'] == 'User updated'

        updatedUser = db.session.get(User, user.id)
        assert updatedUser.username == 'updatedTest'
        assert updatedUser.email == 'test@example.com'

def testDeleteUser(client, auth_token):
    with client.application.app_context():
        user = User(username="test", email="test@example.com")
        db.session.add(user)
        db.session.commit()


        response = client.delete(f'/users/{user.id}', headers={'Authorization': f'Bearer {auth_token}'})
        assert response.status_code == 200
        assert response.json['message'] == 'User deleted'

        deletedUser = db.session.get(User, user.id)
        assert deletedUser is None

def testMissingFieldsTestCreateUser(client):
    response = client.post('/users', json={'email': 'test@example.com'})

    assert response.status_code == 400
    assert response.json['message'] == 'Missing username or email'

def testMissingFieldsUpdateUser(client, auth_token):
    with client.application.app_context():
        user = User(username="test", email="test@example.com")
        db.session.add(user)
        db.session.commit()

        response = client.put(f'/users/{user.id}', json={'email': 'updatedEmail@example.com'}, headers={'Authorization': f'Bearer {auth_token}'})

        assert response.status_code == 400
        assert response.json['message'] == 'Missing username or email'

def testGetInvalidUser(client, auth_token):
    response = client.get('/users/55', headers={'Authorization': f'Bearer {auth_token}'})

    assert response.status_code == 404
    assert response.json['message'] == 'User not found'

def testUpdateInvalidUser(client, auth_token):
    response = client.put('/users/55', json={'username': 'test', 'email': 'test@example.com'}, headers={"Authorization": f'Bearer {auth_token}'})

    assert response.status_code == 404
    assert response.json['message'] == 'User not found'

def testDeleteInvalidUser(client, auth_token):
    response = client.delete('/users/55', headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 404
    assert response.json["message"] == "User not found"