#!/usr/bin/env python
import os

from steam_friends import app


if __name__ == '__main__':
    application = app.create_app(app_env='dev')
    application.config['LOGGING_CONFIG_FUNC']()

    host = os.environ.get("STEAM_FRIENDS_HOST", "localhost")
    port = int(os.environ.get("STEAM_FRIENDS_PORT", 10000))

    application.run(host=host, port=port)
