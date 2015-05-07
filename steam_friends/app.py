import collections

import flask
import steam.api

from steam_friends import models


app = flask.Flask(__name__)


@app.route('/')
def index():
    # todo: this should be from a form
    # todo: need a good way to go from steamid to steamid64
    steamid64s = [
        '76561198060689354',  # ARizzo
        '76561197980747796',  # nynjawitay
        '76561197969428769',  # Son of Themis
        '76561197979664690',  # JC
    ]
    app.logger.info("checking users: %r", steamid64s)

    steam_users = {}
    failed_steamid64s = []
    game_counter = collections.Counter()

    try:
        users_response = steam.api.interface('ISteamUser').GetPlayerSummaries(steamids=steamid64s, version=2)
        for user_data in users_response['response']['players']:
            u = models.SteamUser(**user_data)
            steam_users[u.steamid] = u
    except steam.api.APIError as e:
        app.logger.warning("Steam API Error for users: %s", e)
        failed_steamid64s = steamid64s
    else:
        for u in steam_users.itervalues():
            try:
                games_response = steam.api.interface('IPlayerService').GetOwnedGames(steamid=u.steamid, include_appinfo=1)
                for game_data in games_response['response']['games']:
                    g = models.SteamApp(**game_data)
                    u.games.append(g)
                    game_counter[g] += 1
            except steam.api.APIError as e:
                app.logger.warning("Steam API Error for %s: %s", u, e)
                failed_steamid64s.append(u.steamid)
                continue

    app.logger.debug("steam_users: %s", steam_users)
    # app.logger.debug("game_counter: %s", game_counter)

    return flask.render_template(
        'index.html',
        failed_steamid64s=failed_steamid64s,
        game_counter=game_counter,
        steam_users=steam_users,
    )


if __name__ == '__main__':
    app.debug = True
    app.run()
