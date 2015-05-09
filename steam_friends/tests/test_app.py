from steam_friends import views


def test_app(flask_app):
    assert flask_app.debug is True
    assert flask_app.testing is True
    assert views.blueprint == flask_app.blueprints['steam_friends']
