from pytest import fixture, mark
from app import create_app
from app.routes.api import api_response

@fixture
def app():
    app = create_app()
    return app

@fixture
def app_context(app):
    with app.app_context():
        yield


@mark.parametrize("success, data, error, status_code", [
    (True, {"result": "successful"}, None, 200),
    (False, {"result": "unsuccessful"}, "Unauthorized", 401)
])
def test_api_response(app_context, success, data, error, status_code):
    response = api_response(success=success, data=data, error=error, status_code=status_code)
    response_data = response[0].get_json()
    assert response_data == {"success": success, "data": data, "error": error} and response[1] == status_code


def test_api_response_defaults(app_context):
    response = api_response(success=False, error="Unathorized", status_code=401)
    response_data = response[0].get_json()
    assert response_data == {"success": False, "data": None, "error": "Unathorized"} and response[1] == 401