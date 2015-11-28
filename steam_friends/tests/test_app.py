from __future__ import absolute_import, print_function

import pytest

from steam_friends import app
from steam_friends.views import api, auth, main


def test_app(flask_app):
    assert flask_app.debug is False  # todo: should this be True?
    assert flask_app.secret_key
    assert flask_app.testing is True
    assert api.blueprint == flask_app.blueprints['api']
    assert auth.blueprint == flask_app.blueprints['auth']
    assert main.blueprint == flask_app.blueprints['steam_friends']


def test_app_more_config(monkeypatch):
    key = "TEST_ENV_VAR"
    envvar = "SF_{}".format(key)
    value = "False"

    monkeypatch.setenv(envvar, value)

    flask_app = app.create_app(app_env="test")

    assert flask_app.config.get(key) is False


def test_debug_app(monkeypatch):
    monkeypatch.setenv("SF_DEBUG", "True")

    flask_app = app.create_app(app_env="test")

    assert flask_app.debug is True


def test_bad_app(monkeypatch):
    monkeypatch.setenv("SF_ENV", "")

    with pytest.raises(SystemExit):
        app.create_app()

    with pytest.raises(SystemExit):
        app.create_app(app_env="")
