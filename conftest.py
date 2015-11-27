import logging
import os

# import mockredis
import pytest
import vcr

from steam_friends import app


my_vcr = vcr.VCR(
    cassette_library_dir='data/vcr',
    record_mode=os.environ.get('SF_TEST_RECORD_HTTP', 'none'),
)


@pytest.fixture(autouse=True)
def configure_logs(caplog):
    caplog.setLevel(logging.CRITICAL, logger='vcr.matchers')


@pytest.fixture
def flask_app():
    a = app.create_app(app_env='test')
    assert a.testing is True
    return a


@pytest.fixture
def flask_app_client(flask_app):
    return flask_app.test_client()

"""
@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    # todo: mockredis upstream does not mock from_url :( submit a patch
    mockredis.mock_redis_client.from_url = lambda *args, **kwargs: mockredis.mock_redis_client()
    mockredis.mock_strict_redis_client.from_url = lambda *args, **kwargs: mockredis.mock_strict_redis_client()

    monkeypatch.setattr('redis.Redis', mockredis.mock_redis_client)
    monkeypatch.setattr('redis.StrictRedis', mockredis.mock_strict_redis_client)
"""


def pytest_namespace():
    return {
        'vcr': my_vcr,
    }
