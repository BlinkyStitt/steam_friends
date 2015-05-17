# import logging


class Config(object):
    DEBUG = False
    OPENID_FS_STORE_PATH = "/tmp/steam_friends/openid"

    # todo: remove this and revoke the key. but I'm lazy now
    STEAMODD_API_KEY = "DA0509DA52BC706F282F2D315D3C61BB"

    TESTING = False

    @classmethod
    def LOGGING_CONFIG_FUNC(cls):  # noqa  # todo: make this pretty
        raise NotImplementedError("%s has no LOGGING_CONFIG_FUNC" % cls)


class DevelopmentConfig(Config):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_PROFILER_ENABLED = True
    SECRET_KEY = "not very secret"
    TESTING = False

    """
    @classmethod
    def LOGGING_CONFIG_FUNC(cls):  # noqa: todo: make this pretty
        logging.basicConfig()
    """


class ProductionConfig(Config):
    DEBUG = False
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
