import os
import pytest

from steam_friends import app


@pytest.fixture
def flask_app(monkeypatch):
    steamodd_api_key = os.environ.get('STEAMODD_API_KEY', 'TEST_STEAMODD_API_KEY')
    steam_friends_secret_key = os.environ.get('STEAM_FRIENDS_SECRET_KEY', 'TEST_STEAM_FRIENDS_SECRET_KEY')

    monkeypatch.setenv("STEAMODD_API_KEY", steamodd_api_key)
    monkeypatch.setenv("STEAM_FRIENDS_SECRET_KEY", steam_friends_secret_key)

    a = app.create_app()

    a.debug = True
    a.testing = True

    return a
