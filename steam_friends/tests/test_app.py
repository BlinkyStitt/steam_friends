from steam_friends.views import api, auth, main


def test_app(flask_app):
    assert flask_app.debug is False  # todo: should this be True?
    assert flask_app.secret_key
    assert flask_app.testing is True
    assert api.blueprint == flask_app.blueprints['api']
    assert auth.blueprint == flask_app.blueprints['auth']
    assert main.blueprint == flask_app.blueprints['steam_friends']
