import os

import flask
import steamapi

# commited secrets. yey!
STEAM_API_KEY = os.environ.get("STEAM_API_KEY", "DA0509DA52BC706F282F2D315D3C61BB")


app = flask.Flask(__name__)

STEAM_STATE_MAP = {
    0: "offline/private",
    1: "online",
    2: "busy",
    3: "away",
    4: "snooze",
    5: "looking to trade",
    6: "looking to play",
}


@app.route('/friends')
def friends():
    steamapi.core.APIConnection(api_key=STEAM_API_KEY)

    name = 'nynjawitay'
    steam_user = steamapi.user.SteamUser(userurl=name)

    names = []
    ids = []
    for friend in steam_user.friends:
        if friend.profile_url.startswith('http://steamcommunity.com/id/'):
            names.append(friend.profile_url[len('http://steamcommunity.com/id/'):-1])
        elif friend.profile_url.startswith('http://steamcommunity.com/profiles/'):
            ids.append(friend.profile_url[len('http://steamcommunity.com/profiles/'):-1])

    app.logger.debug("names: %s", names)
    app.logger.debug("ids: %s", ids)

    return 'OK', 200


@app.route('/')
def index():
    steamapi.core.APIConnection(api_key=STEAM_API_KEY)

    # todo: this should be from a form
    people = [
        'ARizzo',
        'nynjawitay',
        '76561197969428769',  # Son of Themis
        '76561197979664690',  # JC
    ]

    steam_names = []
    # todo: counter for games instead of a hard set
    common_games = None

    for name in people:
        app.logger.debug("Checking name: %s", name)

        try:
            steam_user = steamapi.user.SteamUser(userid=int(name))
        except ValueError:
            steam_user = steamapi.user.SteamUser(userurl=name)
        app.logger.debug("steam_user: %r", steam_user)

        try:
            game_names = [g.name for g in steam_user.games]
        except steamapi.errors.APIUnauthorized:
            app.logger.exception("Unable to query user data")
            continue

        if common_games is None:
            common_games = set(game_names)
        else:
            # todo: debug prints?
            common_games = common_games.intersection(game_names)

        steam_names.append(steam_user.name)

    app.logger.debug("common games: %r", common_games)

    return flask.render_template('index.html', steam_names=steam_names, common_games=common_games)


if __name__ == '__main__':
    app.debug = True
    app.run()
