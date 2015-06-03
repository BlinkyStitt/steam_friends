from __future__ import absolute_import

import logging


log = logging.getLogger(__name__)


class Config(object):
    BROKER_URL = 'redis://localhost:10002/1'  # celery queue
    CELERYD_HIJACK_ROOT_LOGGER = False
    DEBUG = False
    LOGGER_NAME = 'flask'
    OPENID_FS_STORE_PATH = "/tmp/steam_friends/openid"
    REDIS_URL = "redis://localhost:10002/0"  # caching

    # todo: remove this and revoke the key. but I'm lazy now
    STEAM_API_KEY = "DA0509DA52BC706F282F2D315D3C61BB"

    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_PROFILER_ENABLED = True
    SECRET_KEY = "not very secret"
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False

    # todo: remove this and revoke the key. but I'm lazy now
    SECRET_KEY = '\xbfCN\xf6\xbfy\xde\xcb~\x19\x1b\xc5\x9dN\x0f"n\x8b\x13$S\xa5\xe7\xd3'

    SERVER_NAME = 'steam.stitthappens.com'
    TESTING = False


class TestingConfig(Config):
    SECRET_KEY = "not very secret"
    TESTING = True


configs = {
    'dev': "{}.{}".format(__name__, 'DevelopmentConfig'),
    'prod': "{}.{}".format(__name__, 'ProductionConfig'),
    'test': "{}.{}".format(__name__, 'TestingConfig'),
}
