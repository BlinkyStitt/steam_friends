import collections

import flask
import steam.api

from steam_friends import models


app = flask.Flask(__name__)


@app.route('/')
def index():
    steamid64s = []

    app.logger.debug('args: %s', flask.request.args)

    steam_users = {}
    failed_users = []
    game_counter = collections.Counter()

    passed_ids = []
    passed_names = []
    use_default_steamid64s = True

    for steamid64 in flask.request.args.getlist('id'):
        use_default_steamid64s = False
        for s in steamid64.split(' '):
            s = s.strip()
            if not s:
                continue
            steamid64s.append(s)
        passed_ids = list(steamid64s)
    for steamid in flask.request.args.getlist('name'):
        use_default_steamid64s = False
        for s in steamid.split(' '):
            s = s.strip()
            if not s:
                continue
            passed_names.append(s)
            steamid64 = models.SteamUser.id_to_id64(s)
            if steamid64:
                steamid64s.append(steamid64)
            else:
                failed_users.append(s)

    passed_ids = ' '.join(passed_ids)
    passed_names = ' '.join(passed_names)

    # if we were only passed names and they all failed lookup, we want to error instead of show default
    if use_default_steamid64s:
        steamid64s = [
            '76561198060689354',  # ARizzo
            '76561197980747796',  # nynjawitay
            '76561197969428769',  # Son of Themis
            '76561197979664690',  # JC
        ]
    app.logger.info("checking users: %r", steamid64s)

    try:
        users_response = steam.api.interface('ISteamUser').GetPlayerSummaries(steamids=steamid64s, version=2)
        for user_data in users_response['response']['players']:
            u = models.SteamUser(**user_data)
            steam_users[u.steamid] = u
    except steam.api.APIError as e:
        app.logger.warning("Steam API Error for users: %s", e)
        failed_users.extend(steamid64s)
        flask.flash("Failed connecting to the steam API", "danger")
    else:
        if len(steam_users) == 0:
            flask.flash("No users found!", "danger")
        elif len(steam_users) < 2:
            flask.flash("This app works a lot better with more than 2 users.", "info")

        for u in steam_users.itervalues():
            try:
                games_response = steam.api.interface('IPlayerService').GetOwnedGames(steamid=u.steamid, include_appinfo=1)
                for game_data in games_response['response']['games']:
                    g = models.SteamApp(**game_data)
                    u.games.append(g)
                    game_counter[g] += 1
            except (KeyError, steam.api.APIError) as e:
                app.logger.warning("Error while querying for games for %s: %s", u, e)
                failed_users.append(u.steamid)
                continue

    return flask.render_template(
        'index.html',
        failed_users=failed_users,
        game_counter=game_counter,
        passed_ids=passed_ids,
        passed_names=passed_names,
        steam_users=steam_users,
    )
