import os
import pytest

from steam_friends import app


@pytest.fixture
def flask_app(monkeypatch):
    a = app.create_app(app_env='test')

    a.debug = True
    a.testing = True

    return a
