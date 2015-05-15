import steam_friends.app

application = steam_friends.app.create_app(app_env='prod')
print "Loaded", application
