#!/usr/bin/env python
import os

import steam_friends.app


if __name__ == '__main__':
    app = steam_friends.app.create_app(app_env='dev')

    host = os.environ.get("STEAM_FRIENDS_HOST", "localhost")
    port = int(os.environ.get("STEAM_FRIENDS_PORT", 10000))

    app.run(host=host, port=port)
