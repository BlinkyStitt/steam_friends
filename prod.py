"""
this file is used to run the flask application in production
"""
from __future__ import absolute_import

import logging
import sys

from steam_friends import app


# a simple single line format suitable for production
log_format = '%(asctime)s - %(levelname)s - %(name)s: %(message)s'

# configure logging before we do anything
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=log_format)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# uwsgi expects "application" by default
application = app.create_app(app_env='prod')

# assert some things just to be safe
assert application.debug is False
assert application.testing is False

application.logger.info("Starting %s for production", application)
