from steam_friends import app

application = app.create_app(app_env='prod')

# just to be safe
assert application.debug is False
assert application.testing is False

application.config['LOGGING_CONFIG_FUNC']()
