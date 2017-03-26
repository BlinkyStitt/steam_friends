from __future__ import absolute_import, print_function

# todo: make sure we exit if our config has this in it
SECRET = RuntimeError('__SECRET__PUT_THIS_IN_YOUR_ENV__')


class Config(object):
    BROKER_URL = 'redis://redis:6379/1'  # celery queue
    CELERYD_HIJACK_ROOT_LOGGER = False
    DEBUG = False
    LOGGER_NAME = 'flask'
    OPENID_FS_STORE_PATH = "/src/data/openid"
    REDIS_URL = "redis://redis:6379/0"  # caching
    SECRET_KEY = "not very secret"
    STEAM_API_KEY = SECRET
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_PROFILER_ENABLED = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = SECRET
    SERVER_NAME = 'steam.stitthappens.com'
    TESTING = False


class TestingConfig(Config):
    TESTING = True


configs = {
    'dev': "{}.{}".format(__name__, 'DevelopmentConfig'),
    'prod': "{}.{}".format(__name__, 'ProductionConfig'),
    'test': "{}.{}".format(__name__, 'TestingConfig'),
}
