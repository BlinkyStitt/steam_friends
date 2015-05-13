from __future__ import print_function

import flask
import os
import sys

from werkzeug.contrib import fixers
import steam  # https://github.com/Lagg/steamodd

from steam_friends import config, ext, views


def create_app(app_env=None):
    app = flask.Flask('steam_friends')

    # load main configs
    try:
        app_env = app_env or os.environ['STEAM_FRIENDS_ENV']
    except KeyError:
        print("ERROR: You must `export STEAM_FRIENDS_ENV=dev`", file=sys.stderr)
        sys.exit(1)

    app_config = config.configs[app_env]
    app.config.from_object(app_config)

    # allow loading additional configuration
    # secret things like passwords and API keys are loaded here
    app.config.from_envvar('STEAM_FRIENDS_CONFIG', silent=True)

    # anything can also come from env vars
    for key, value in os.environ.iteritems():
        if key.startswith('STEAM_FRIENDS_'):
            config_key = key[len('STEAM_FRIENDS_'):]
            app.config[config_key] = value

    # setup apis and extensions
    steam.api.key.set(app.config['STEAMODD_API_KEY'])
    ext.cache.init_app(app)
    ext.oid.init_app(app)

    # attach our blueprints
    app.register_blueprint(views.blueprint)

    # dev only things go here
    if app.debug:
        from flask_debugtoolbar import DebugToolbarExtension

        app.config['DEBUG_TB_PROFILER_ENABLED'] = True
        # app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True

        DebugToolbarExtension(app)

    # fix the IP when behind an nginx proxy
    if app.config.get('PROXY_FIX'):
        app.wsgi_app = fixers.ProxyFix(app.wsgi_app)

    return app
