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

        self.games = []
        self.friends = []

    def __str__(self):
        return self.personaname

    def __repr__(self):
        return "{cls}(steamid='{steamid}', personaname='{personaname}', num_games={num_games})".format(
            cls=self.__class__.__name__,
            steamid=self.steamid,
            personaname=self.personaname,
            num_games=len(self.games),
        )

    @classmethod
    def id_to_id64(cls, steamid):
        r = steam.api.interface('ISteamUser').ResolveVanityURL(vanityurl=steamid)
        try:
            return r['response']['steamid']
        except (KeyError, steam.api.HTTPError):
            return None
