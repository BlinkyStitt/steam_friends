from __future__ import print_function

import logging
import os
import sys

from flask_debugtoolbar import DebugToolbarExtension
import flask
import steam  # https://github.com/Lagg/steamodd

from steam_friends import config, ext
from steam_friends.views import api, auth, main


log = logging.getLogger(__name__)


def internal_error(e):
    error_message = "Caught unhandled exception: {}".format(e)
    # flask does this logging in handle_user_exception
    # log.exception(error_message)
    return flask.render_template('500.html', error_message=error_message), 500


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

    # setup apis and extensions
    steam.api.key.set(app.config['STEAMODD_API_KEY'])
    ext.cache.init_app(app)
    ext.oid.init_app(app)

    # attach our blueprints
    map(app.register_blueprint, [
        api.blueprint,
        auth.blueprint,
        main.blueprint,
    ])

    # setup application wide error handlers
    # other error handlers should be attached to their respective blueprints
    app.error_handler_spec[None][500] = internal_error

    # dev only things go here
    if app.debug:
        DebugToolbarExtension(app)

    return app
