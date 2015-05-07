#!/usr/bin/env python
import os

from werkzeug.contrib.fixers import ProxyFix

from steam_friends.app import app


if __name__ == '__main__':
    if not os.environ.get("STEAMODD_API_KEY"):
        # http://steamcommunity.com/dev/apikey
        raise ValueError("You must export STEAMODD_API_KEY")
    if os.environ.get("STEAM_FRIENDS_SECRET_KEY"):
        app.secret_key = True
    else:
        # used for signing cookies
        raise ValueError("You must export STEAM_FRIENDS_SECRET_KEY")

    if os.environ.get("STEAM_FRIENDS_DEBUG"):
        app.debug = True

    host = os.environ.get("STEAM_FRIENDS_HOST", "127.0.0.1")
    port = int(os.environ.get("STEAM_FRIENDS_PORT", 10000))

    if os.environ.get("STEAM_FRIENDS_PROXY_FIX"):
        app.wsgi_app = ProxyFix(app.wsgi_app)

    app.run(host=host, port=port)
