from steam_friends import app

application = app.create_app(app_env='prod')
application.config['LOGGING_CONFIG_FUNC']()
