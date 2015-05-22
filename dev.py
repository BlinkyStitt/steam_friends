#!/usr/bin/env python
import logging
import os
import sys

import flask

from steam_friends import app


# configure logging before we do anything
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=flask.Flask.debug_log_format)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# these things aren't in application.config
host = os.environ.get("STEAM_FRIENDS_HOST", "localhost")
port = int(os.environ.get("STEAM_FRIENDS_PORT", 10000))

application = app.create_app(app_env='dev')

application.logger.info("Starting %s for development at http://%s:%s", application, host, port)
if application.debug:
    application.logger.warning("Application debugging enabled! Be sure not to expose this to the Internet!")

application.run(host=host, port=port)
