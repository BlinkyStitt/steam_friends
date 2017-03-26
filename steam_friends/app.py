from __future__ import absolute_import, print_function

import os
import sys

import flask_debugtoolbar
import celery
import flask

from steam_friends import config, ext
from steam_friends.views import api, auth, main


@celery.signals.setup_logging.connect
def celery_logging(*args, **kwargs):
    # stop celery from hijacking the logger
    pass


def create_app(app_env=None):
    app = flask.Flask('steam_friends')

    # load main configs
    try:
        app_env = app_env or os.environ['SF_ENV']
        app_config = config.configs[app_env]
    except KeyError:
        # print because logging can't be setup yet
        print("ERROR: You must `export SF_ENV` to one of: {}".format(', '.join(config.configs.iterkeys())), file=sys.stderr)
        sys.exit(1)
    app.config.from_object(app_config)

    # allow loading additional configuration
    # secret things like passwords and API keys are loaded here
    app.config.from_envvar('SF_CONFIG', silent=True)

    # anything can also come from env vars
    # SECRETS can only come from environment variables
    for key, value in os.environ.iteritems():
        if key.startswith('SF_'):
            config_key = key[len('SF_'):]

            # I don't love this...
            if value == 'True':
                value = True
            elif value == 'False':
                value = False

            app.config[config_key] = value

    # all secrets should have been replaced with real values. check for any missed ones
    for key, value in app.config.iteritems():
        if key == config.SECRET:
            raise ValueError("SF_{} not set!" % key)

    ext.flask_celery.init_app(app)
    ext.flask_redis.init_app(app)
    ext.oid.init_app(app)

    # attach our blueprints
    map(app.register_blueprint, [
        auth.blueprint,
        main.blueprint,
    ])
    app.register_blueprint(api.blueprint, url_prefix='/api')

    # setup application wide error handlers
    # other error handlers should be attached to their respective blueprints
    # TODO: i think new flask changed this
#    app.error_handler_spec[None][500] = main.internal_error

    # dev only things go here
    if app.debug:
        flask_debugtoolbar.DebugToolbarExtension(app)

    # delete flask's default handlers. https://github.com/mitsuhiko/flask/issues/641
    # we configure our own logging when we want it
    del app.logger.handlers[:]

    return app
