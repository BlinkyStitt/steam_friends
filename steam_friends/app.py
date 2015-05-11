import flask
import os

from werkzeug.contrib import fixers

from steam_friends import ext, views


def create_app():
    app = flask.Flask('steam_friends')

    app.config['CACHE_TYPE'] = 'simple'

    if not os.environ.get("STEAMODD_API_KEY"):
        # http://steamcommunity.com/dev/apikey
        raise ValueError("You must export STEAMODD_API_KEY")

    # used for signing cookies
    secret_key = os.environ.get("STEAM_FRIENDS_SECRET_KEY")
    if secret_key:
        app.secret_key = secret_key
    else:
        raise ValueError("You must export STEAM_FRIENDS_SECRET_KEY")

    if os.environ.get("STEAM_FRIENDS_DEBUG") == "1":
        from flask_debugtoolbar import DebugToolbarExtension

        app.debug = True
        app.config['DEBUG_TB_PROFILER_ENABLED'] = True
        # app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True

        DebugToolbarExtension(app)

    if os.environ.get("STEAM_FRIENDS_PROXY_FIX") == "1":
        app.wsgi_app = fixers.ProxyFix(app.wsgi_app)

    ext.cache.init_app(app)
    ext.oid.init_app(app)

    app.register_blueprint(views.blueprint)

    return app
