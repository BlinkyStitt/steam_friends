#!/usr/bin/env python
import logging
import os
import sys

from steam_friends import app


application = app.create_app(app_env='dev')

# shut up the flask logger
application.logger
del logging.getLogger(application.logger_name).handlers[:]

# configure with our log format
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=application.debug_log_format)

# lower level on 3rd party modules
logging.getLogger('werkzeug').setLevel(logging.WARNING)

application.logger.info("Starting %s for development", application)

# these things aren't in the config
host = os.environ.get("STEAM_FRIENDS_HOST", "localhost")
port = int(os.environ.get("STEAM_FRIENDS_PORT", 10000))

# do the thing
application.run(host=host, port=port)
