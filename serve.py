#!/usr/bin/env python
import os

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

    app.run()
