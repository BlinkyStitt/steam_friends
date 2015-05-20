import logging
import sys


log = logging.getLogger(__name__)

# copied from flask.logging for now
PROD_LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s: %(message)s'
DEBUG_LOG_FORMAT = (
    '-' * 80 + '\n' +
    '%(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n' +
    '%(message)s\n' +
    '-' * 80
)


class Config(object):
    DEBUG = False
    LOGGER_HANDLER_POLICY = 'debug'
    LOGGER_NAME = 'flask'
    OPENID_FS_STORE_PATH = "/tmp/steam_friends/openid"

    # todo: remove this and revoke the key. but I'm lazy now
    STEAMODD_API_KEY = "DA0509DA52BC706F282F2D315D3C61BB"

    TESTING = False

    @classmethod
    def _configure_logging(cls):
        """Setup loggers to send most everything to stderr.

        .. TODO:: using classmethods and _functions as part of config doesn't seem like the best way to setup logging
        """
        # shut up the flask logger
        # todo: not sure this will work with overrides from the environment
        del logging.getLogger(cls.LOGGER_NAME).handlers[:]

        # configure with our log format
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=DEBUG_LOG_FORMAT)

        # lower level on 3rd party modules
        logging.getLogger('werkzeug').setLevel(logging.WARNING)

        log.debug("Basic logging configured")
    LOGGING_CONFIG_FUNC = _configure_logging


class DevelopmentConfig(Config):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_PROFILER_ENABLED = True
    SECRET_KEY = "not very secret"
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    LOGGER_HANDLER_POLICY = 'production'
    SECRET_KEY = '\xbfCN\xf6\xbfy\xde\xcb~\x19\x1b\xc5\x9dN\x0f"n\x8b\x13$S\xa5\xe7\xd3'
    SERVER_NAME = 'steam.stitthappens.com'
    TESTING = False

    # using classmethods and _functions doesn't seem like the best way to setup logging
    @classmethod
    def _configure_logging(cls):
        """Setup loggers to send most everything to stderr.

        .. TODO:: using classmethods and _functions as part of config doesn't seem like the best way to setup logging
        """
        del logging.getLogger(cls.LOGGER_NAME).handlers[:]

        # configure with our log format
        # todo: lower log level and format verbosity
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=DEBUG_LOG_FORMAT)

        # lower level on 3rd party modules
        logging.getLogger('werkzeug').setLevel(logging.WARNING)

        log.debug("Basic logging configured")
    LOGGING_CONFIG_FUNC = _configure_logging


class TestingConfig(Config):
    SECRET_KEY = "not very secret"
    TESTING = True


configs = {
    'dev': "{}.{}".format(__name__, 'DevelopmentConfig'),
    'prod': "{}.{}".format(__name__, 'ProductionConfig'),
    'test': "{}.{}".format(__name__, 'TestingConfig'),
}
