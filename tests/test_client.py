from pytest import fixture, mark
from app import create_app

@fixture
def app():
    app = create_app()
    return app

@fixture
def client(app):
    client = app.test_client()
    return client

def test_user_api(client):
    response = client.get('/api/user')
    response_data = response.get_json()
    assert response_data == {"success": False, "data": None, "error": "Unauthorized"} and response.status_code == 401

def test_authorized_user_api(client):
    with client.session_transaction() as session:
        session['user'] = {
            'id': 123,
            'db_id': 123,
            'login': 'test_login',
            'display_name': 'test_name',
            'profile_image_url': 'test_url'
        }
        session['access_token'] = "test_token"
    response = client.get('/api/user')
    response_data = response.get_json()
    assert response_data == {
        "success": True,
        "data": {
            "user": {
                'id': 123,
                'db_id': 123,
                'login': 'test_login',
                'display_name': 'test_name',
                'profile_image_url': 'test_url'
                }
            },
            "error": None
        } and response.status_code == 200