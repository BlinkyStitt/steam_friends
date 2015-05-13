class Config(object):
    DEBUG = False
    TESTING = False

    # todo: remove this and revoke the key. but I'm lazy now
    STEAMODD_API_KEY = "DA0509DA52BC706F282F2D315D3C61BB"


class DevelopmentConfig(Config):
    DEBUG = True
    DEBUG_TB_PROFILER_ENABLED = True
    SECRET_KEY = "not very secret"


class ProductionConfig(Config):
    DEBUG = True
    PROXY_FIX = True

    # todo: remove this and revoke the key. but I'm lazy now
    SECRET_KEY = "not secret enough"


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "not very secret"


configs = {
    'dev': "{}.{}".format(__name__, 'DevelopmentConfig'),
    'prod': "{}.{}".format(__name__, 'ProductionConfig'),
    'test': "{}.{}".format(__name__, 'TestingConfig'),
}
