import collections
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
    users = [
        'nynjawitaynynjawitaynynjawitay',
        'ARizzo',
        'nynjawitay',
        '76561197969428769',  # Son of Themis
        '76561197979664690',  # JC
    ]
    app.logger.info("checking users: %r", users)

    steam_users = []
    failed_steam_users = []
    game_counter = collections.Counter()

    for user_id in users:
        app.logger.debug("Checking user_id: %s", user_id)

        try:
            steam_user = steamapi.user.SteamUser(userid=int(user_id))
        except (steamapi.user.UserNotFoundError, ValueError):
            try:
                steam_user = steamapi.user.SteamUser(userurl=user_id)
            except steamapi.user.UserNotFoundError:
                app.logger.warning("User not found: %s", user_id)
                failed_steam_users.append(user_id)
                continue
        try:
            game_counter.update(steam_user.games)
        except steamapi.errors.APIUnauthorized:
            app.logger.exception("Access denied querying game list: %s", user_id)
            failed_steam_users.append(user_id)
            continue

        steam_users.append(steam_user)

    return flask.render_template(
        'index.html',
        failed_steam_users=failed_steam_users,
        game_counter=game_counter,
        steam_users=steam_users,
    )


if __name__ == '__main__':
    app.debug = True
    app.run()
