#!/usr/bin/env python
import os

import steam_friends.app


if __name__ == '__main__':
    if not os.environ.get("STEAMODD_API_KEY"):
        raise ValueError("You must export STEAMODD_API_KEY")

    steam_friends.app.app.debug = True
    steam_friends.app.app.run()
