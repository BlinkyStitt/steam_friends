import collections
import os

import flask
import steam.api


if not os.environ.get("STEAMODD_API_KEY"):
    raise ValueError("You must export STEAMODD_API_KEY")


app = flask.Flask(__name__)


class SteamApp(object):

    image_url = "http://media.steampowered.com/steamcommunity/public/images/apps/{appid}/{hash}.jpg"

    def __init__(self, **kwargs):
        self.appid = kwargs['appid']
        self.name = kwargs['name'].encode('ascii', 'ignore')  # todo: what should we do here?
        self.img_logo_url = self.image_url.format(
            appid=self.appid,
            hash=kwargs['img_logo_url'],
        )
        self.img_icon_url = self.image_url.format(
            appid=self.appid,
            hash=kwargs['img_icon_url'],
        )
        # there are more attributes than this, but we don't need them

    def __eq__(self, other):
        app.logger.debug("checking equality")
        return self.appid == other.appid

    def __hash__(self):
        return hash(self.appid)

    def __repr__(self):
        return "{cls}(appid={appid}, name={name})".format(
            cls=self.__class__.__name__,
            appid=self.appid,
            name=self.name,
        )

    def __str__(self):
        return self.name


class SteamUser(object):

    def __init__(self, **kwargs):
        self.avatar = kwargs['avatar']
        self.avatarmedium = kwargs['avatarmedium']
        self.avatarfull = kwargs['avatarfull']
        self.steamid = kwargs['steamid']
        self.personaname = kwargs['personaname']
        self.personastate = kwargs['personastate']

        self.games = []

    def __str__(self):
        return self.personaname

    def __repr__(self):
        return "{cls}(steamid='{steamid}', personaname='{personaname}', num_games={num_games})".format(
            cls=self.__class__.__name__,
            steamid=self.steamid,
            personaname=self.personaname,
            num_games=len(self.games),
        )


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
            u = SteamUser(**user_data)
            steam_users[u.steamid] = u
    except steam.api.APIError as e:
        app.logger.warning("Steam API Error for users: %s", e)
        failed_steamid64s = steamid64s
    else:
        for u in steam_users.itervalues():
            try:
                games_response = steam.api.interface('IPlayerService').GetOwnedGames(steamid=u.steamid, include_appinfo=1)
                for game_data in games_response['response']['games']:
                    g = SteamApp(**game_data)
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
