import pytest

from steam_friends import app


@pytest.fixture
def flask_app():
    a = app.create_app(app_env='test')
    assert a.testing is True
    return a


@pytest.fixture
def flask_app_client(flask_app):
    return flask_app.test_client()
