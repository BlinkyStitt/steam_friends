#!/usr/bin/env python
import os

from steam_friends.app import create_app


if __name__ == '__main__':
    host = os.environ.get("STEAM_FRIENDS_HOST", "127.0.0.1")
    port = int(os.environ.get("STEAM_FRIENDS_PORT", 10000))

    create_app().run(host=host, port=port)
