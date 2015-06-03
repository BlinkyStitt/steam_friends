from __future__ import absolute_import
from __future__ import print_function

import logging
import os
import sys

from flask.ext import debugtoolbar
import celery
import flask

from steam_friends import config, ext
from steam_friends.views import api, auth, main


log = logging.getLogger(__name__)


@celery.signals.setup_logging.connect
def celery_logging(*args, **kwargs):
    # stop celery from hijacking the logger
    pass


def create_app(app_env=None):
    app = flask.Flask('steam_friends')

    # load main configs
    try:
        app_env = app_env or os.environ['STEAM_FRIENDS_ENV']
        app_config = config.configs[app_env]
    except KeyError:
        # print because logging can't be setup yet
        print("ERROR: You must `export STEAM_FRIENDS_ENV` to one of: {}".format(', '.join(config.configs.iterkeys())), file=sys.stderr)
        sys.exit(1)
    app.config.from_object(app_config)

    # allow loading additional configuration
    # secret things like passwords and API keys are loaded here
    app.config.from_envvar('STEAM_FRIENDS_CONFIG', silent=True)

    # anything can also come from env vars
    for key, value in os.environ.iteritems():
        if key.startswith('STEAM_FRIENDS_'):
            config_key = key[len('STEAM_FRIENDS_'):]

            # I don't love this...
            if value == 'True':
                value = True
            elif value == 'False':
                value = False

            app.config[config_key] = value

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
    app.error_handler_spec[None][500] = main.internal_error

    # dev only things go here
    if app.debug:
        debugtoolbar.DebugToolbarExtension(app)

    # delete flask's default handlers. https://github.com/mitsuhiko/flask/issues/641
    # we configure our own logging when we want it
    del app.logger.handlers[:]

    return app
