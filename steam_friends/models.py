import flask

import steam.api


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

        # these are lazy loaded
        self._friends = None
        self._games = None

    def __eq__(self, other):
        return self.steamid == other.steamid

    def __hash__(self):
        return hash(self.steamid)

    def __str__(self):
        return self.personaname

    def __repr__(self):
        return "{cls}(steamid='{steamid}', personaname='{personaname}', num_games={num_games})".format(
            cls=self.__class__.__name__,
            steamid=self.steamid,
            personaname=self.personaname,
            num_games=len(self.games),
        )

    @property
    def friends(self, relationship='friend'):
        if self._friends is None:
            f = []

            # todo: only lookup friends that aren't in our cache

            friends_response = steam.api.interface('ISteamUser').GetFriendList(
                steamid=self.steamid,
                relationship=relationship,
            )
            try:
                for friends_data in friends_response['friendslist']['friends']:
                    f.append(friends_data['steamid'])
            except steam.api.HTTPError:
                flask.current_app.logger.warning("Failed fetching friends for %s", self)
            self._friends = self.get_users(f)
        return self._friends

    @property
    def games(self, include_appinfo=1, include_played_free_games=1):
        if self._games is None:
            g = []

            # todo: only lookup games that aren't in our cache

            games_response = steam.api.interface('IPlayerService').GetOwnedGames(
                steamid=self.steamid,
                include_appinfo=include_appinfo,
                include_played_free_games=include_played_free_games,
            )
            if games_response['response'] == {}:
                flask.current_app.logger.warning("Failed fetching games for %s", self)
            else:
                for game_data in games_response['response']['games']:
                    g.append(SteamApp(**game_data))
            self._games = g
        return self._games

    @classmethod
    def get_user(cls, steamid64):
        return cls.get_users(steamid64)[0]

    @classmethod
    def get_users(cls, steamid64s):
        steam_users = []  # todo: maybe make this a dict

        # todo: only lookup users that aren't in our cache

        users_response = steam.api.interface('ISteamUser').GetPlayerSummaries(
            steamids=steamid64s,
            version=2,
        )
        for user_data in users_response['response']['players']:
            u = cls(**user_data)
            flask.current_app.logger.debug("user: %r", u)
            steam_users.append(u)
        return steam_users

    @classmethod
    def id_from_openid(cls, claim_id):
        if not claim_id.startswith('http://steamcommunity.com/openid/id/'):
            raise ValueError("claim_id not from steamcommunity.com")
        return claim_id[len('http://steamcommunity.com/openid/id/'):]

    @classmethod
    def id_to_id64(cls, steamid):
        # todo: cache this
        r = steam.api.interface('ISteamUser').ResolveVanityURL(vanityurl=steamid)
        try:
            return r['response']['steamid']
        except (KeyError, steam.api.HTTPError):
            return None
