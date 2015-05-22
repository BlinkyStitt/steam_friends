import logging
import sys

from steam_friends import app


log_format = '%(asctime)s - %(levelname)s - %(name)s: %(message)s'

# uwsgi expects "application" by default
application = app.create_app(app_env='prod')

# assert some things just to be safe
assert application.debug is False
assert application.testing is False

# delete flask's default logger
application.logger
del logging.getLogger(application.logger_name).handlers[:]

# todo: lower log level and format verbosity
logging.basicConfig(stream=sys.stderr, level=logging.WARNING, format=log_format)

# lower level on 3rd party modules
logging.getLogger('werkzeug').setLevel(logging.WARNING)

application.logger.info("Starting %s for production", application)
