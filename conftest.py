import os

import pytest
import vcr

from steam_friends import app


my_vcr = vcr.VCR(
    cassette_library_dir='data/vcr',
    record_mode=os.environ.get('STEAM_FRIENDS_TEST_RECORD_HTTP', 'none'),
)


@pytest.fixture
def flask_app():
    a = app.create_app(app_env='test')
    assert a.testing is True
    return a


@pytest.fixture
def flask_app_client(flask_app):
    return flask_app.test_client()


def pytest_namespace():
    return {
        'vcr': my_vcr,
    }
