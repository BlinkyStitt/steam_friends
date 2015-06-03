import os

import pytest
import vcr

from steam_friends import app


if os.environ.get('STEAM_FRIENDS_TEST_RECORD_HTTP') == '1':
    record_mode = 'all'
else:
    record_mode = 'none'


my_vcr = vcr.VCR(
    cassette_library_dir='data/vcr',
    record_mode=record_mode,
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
