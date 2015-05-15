import steam_friends.app

app = steam_friends.app.create_app(app_env='prod')

print list(app.url_map.iter_rules())
