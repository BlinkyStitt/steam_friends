from __future__ import absolute_import

import functools
import logging
import msgpack
import random
import string

import flask
import requests

from steam_friends import exc, ext, steam_api


log = logging.getLogger(__name__)

DEFAULT_TTL = 3600


def cached_property(func):
    """Cache results of the func in the request global"""
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if hasattr(flask.g, 'cached_property'):
            cache = flask.g.cached_property
        else:
            cache = flask.g.cached_property = {}

        # todo: do this fast and make sure we properly order dicts
        key = func.__name__ + str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]
    return inner


@functools.total_ordering
class SteamApp(object):

    image_url = "http://media.steampowered.com/steamcommunity/public/images/apps/{appid}/{hash}.jpg"

    # these appids don't seem to have store pages but are still returned in games lists...
    # todo: figure out what all these actually are if they aren't games
    skipped_appids = (
        '2430',
        '12170',
        '12180',
        '12230',
        '12240',
        '12250',
        '18110',
        '201280',
        '205790',
        '219540',
        '223530',
        '228200',
        '28050',
        '367540',
        '44320',
    )

    def __init__(self, appid, queue_details=False, **kwargs):
        self._img_icon_hash = self._img_logo_hash = self._name = None

        self.appid = appid

        # this may have been given, or it may come from appdetails
        self.name = kwargs.pop('name', None)

        # these are actually just hashes and not full urls if they come from the steam api
        # setting them sets the cache. setting them to None queries the cache
        self.img_logo_hash = kwargs.pop('img_logo_hash', kwargs.pop('img_logo_url', None))
        self.img_icon_hash = kwargs.pop('img_icon_hash', kwargs.pop('img_icon_url', None))

        if queue_details:
            try:
                # pre-emptively fill caches
                # task_id = get_app_details.delay(self.steamid)  # this should work, but it misses our config :'(
                task_id = ext.flask_celery.get_task('get_app_details').delay(self.appid)
                log.debug("queued get_app_details(%s): %s", self.appid, task_id)
            except Exception as e:
                log.warning("Unable to queue get_app_details: %s", e)

        # log.debug("extra args for %r: %s", self, kwargs)

    def __eq__(self, other):
        try:
            return self.appid == other.appid
        except AttributeError:
            return False

    def __lt__(self, other):
        return self.name < other.name

    def __hash__(self):
        return hash(self.appid)

    def __repr__(self):
        # we can't include self.name in this because steam api may have been rate limited
        return "{cls}(appid={appid})".format(
            cls=self.__class__.__name__,
            appid=self.appid,
        )

    def __str__(self):
        return self.name

    @property
    def app_details_key(self):
        return "{!r}:app_details".format(self, self.appid)

    @cached_property
    def app_details(self):
        if self.appid in self.skipped_appids:
            return

        cache_key = self.app_details_key
        cached_app_details = ext.flask_redis.get(cache_key)
        if cached_app_details:
            cached_app_details = msgpack.loads(cached_app_details)
            log.debug("Retrieved app_details for %r from cache", self)
        else:
            try:
                # eventhough this says "appids", it returns null when given multiple values
                # this is an undocumented api endpoint used by steam big picture
                r = requests.get("http://store.steampowered.com/api/appdetails/", params={
                    'appids': self.appid,
                })
            except requests.exceptions.ConnectionError as e:
                log.error("%s", e)
                # todo: flash message?
            else:
                try:
                    app_json = r.json()[str(self.appid)]
                except (TypeError, KeyError):
                    app_json = None

                # sometimes we get back "null" sometimes "success == failed"
                if not app_json or 'success' not in app_json or not app_json['success']:
                    # todo: double check that r.url is a thing
                    log.warning("Failed querying %s: %s", r.url, r.text)
                    return

                cached_app_details = app_json['data']
                ext.flask_redis.set(cache_key, msgpack.dumps(cached_app_details), ex=DEFAULT_TTL)

        return cached_app_details

    @property
    def img_icon_hash_key(self):
        return "{!r}:img_icon_hash".format(self, self.appid)

    @property
    def img_icon_hash(self):
        if self._img_icon_hash is None:
            self._img_icon_hash = ext.flask_redis.get(self.img_icon_hash_key)
        return self._img_icon_hash

    @img_icon_hash.setter
    def img_icon_hash(self, value):
        if value is not None:
            ext.flask_redis.set(self.img_icon_hash_key, value, ex=DEFAULT_TTL)
        self._img_icon_hash = value

    @property
    def img_icon_url(self):
        if not self.img_icon_hash:
            return
        return self.image_url.format(
            appid=self.appid,
            hash=self.img_icon_hash,
        )

    @property
    def img_logo_hash_key(self):
        return "{!r}:img_logo_hash".format(self, self.appid)

    @property
    def img_logo_hash(self):
        if self._img_logo_hash is None:
            self._img_logo_hash = ext.flask_redis.get(self.img_logo_hash_key)
        return self._img_logo_hash

    @img_logo_hash.setter
    def img_logo_hash(self, value):
        if value is not None:
            ext.flask_redis.set(self.img_logo_hash_key, value, ex=DEFAULT_TTL)
        self._img_logo_hash = value

    @property
    def img_logo_url(self):
        if not self.img_logo_hash:
            return
        return self.image_url.format(
            appid=self.appid,
            hash=self.img_logo_hash,
        )

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value is None:
            if self.app_details:
                value = self.app_details['name']
            else:
                # todo: not sure about this
                raise exc.SteamApiException("Could not find name for %r" % self)

        self._name = ''.join(s for s in value if s in string.printable)  # todo: support non-ascii?

    def to_dict(self, with_details=False):
        data = {
            'appid': self.appid,
            'name': self.name,
            'img_logo_url': self.img_logo_url,
            'img_icon_url': self.img_icon_url,
        }
        if with_details:
            data['app_details'] = self.app_details
        return data


@functools.total_ordering
class SteamUser(object):

    def __init__(self, steamid, queue_friends_of_friends=False, **kwargs):
        self.steamid = steamid  # this should probably be named steamid64 but then it wont match steam's api

        self.avatar = kwargs.pop('avatar', None)
        self.avatarmedium = kwargs.pop('avatarmedium', None)
        self.avatarfull = kwargs.pop('avatarfull', None)

        personaname = kwargs.pop('personaname', '')
        self.personaname = ''.join(s for s in personaname if s in string.printable)  # todo: support non-ascii?

        self.personastate = kwargs.pop('personastate', None)

        if queue_friends_of_friends:
            try:
                # pre-emptively fill caches
                # task_id = get_friends_of_friends.delay(self.steamid)  # this should work, but it misses our config
                task_id = ext.flask_celery.get_task('get_friends_of_friends').delay(self.steamid)
                log.debug("queued get_friends_of_friends(%s): %s", self.steamid, task_id)
            except Exception as e:
                # todo: wtf is going on here?! why is this using the normal config
                log.exception("Unable to queue get_friends_of_friends: %s", e)

    def __eq__(self, other):
        try:
            return self.steamid == other.steamid
        except AttributeError:
            return False

    def __lt__(self, other):
        try:
            return self.personaname < other.personaname
        except AttributeError:
            return False

    def __hash__(self):
        return hash(self.steamid)

    def __str__(self):
        return self.personaname

    def __repr__(self):
        # we can't include self.personaname in this because steam api may have been rate limited
        return "{cls}(steamid='{steamid}')".format(
            cls=self.__class__.__name__,
            steamid=self.steamid,
        )

    @property
    def friends(self):
        return self.get_friends()

    @cached_property
    def get_friends(self, queue_friends_of_friends=False, relationship='friend'):
        cache_key = repr(self) + ':get_friends'

        f_ids = ext.flask_redis.get(cache_key)
        if f_ids:
            f_ids = msgpack.loads(f_ids)
            log.info("Found cached friends of %r: %s", self, f_ids)
        else:
            log.info("Fetching friends of %r", self)
            r = steam_api.get_json(
                "ISteamUser/GetFriendList",
                steamid=self.steamid,
            )

            f_ids = []
            if r:
                for friends_data in r['friendslist']['friends']:
                    f_ids.append(friends_data['steamid'])
                log.debug("Found friends of %r: %s", self, f_ids)
                ext.flask_redis.set(cache_key, msgpack.dumps(f_ids), ex=DEFAULT_TTL)
            else:
                log.warning("Failed fetching friends of %r", self)

        return self.get_users(f_ids, queue_friends_of_friends=queue_friends_of_friends)

    @property
    def games(self):
        return self.get_games()

    @cached_property
    def get_games(self, include_appinfo=1, include_played_free_games=1, queue_details=0):
        cache_key = "{!r}:get_games:{}:{}".format(self, include_appinfo, include_played_free_games)

        # todo: just cache the game ids and let the icon hashes be cached elsewhere
        game_datas = ext.flask_redis.get(cache_key)
        if game_datas:
            game_datas = msgpack.loads(game_datas)
        else:
            game_datas = []

            log.info("Fetching games of %r", self)
            # this seem to be the onl place we can get the icon and logo hashes
            games_json = steam_api.get_json(
                "IPlayerService/GetOwnedGames",
                include_appinfo=include_appinfo,
                include_played_free_games=include_played_free_games,
                steamid=self.steamid,
            )
            if games_json and games_json['response']:
                for game_data in games_json['response']['games']:
                    # todo: sometimes string, sometimes int...
                    if str(game_data['appid']) in SteamApp.skipped_appids:
                        continue

                    game_datas.append({
                        'appid': game_data['appid'],
                        'name': ''.join(s for s in game_data['name'] if s in string.printable),  # todo: support non-ascii?
                        'img_icon_hash': game_data['img_icon_url'],
                        'img_logo_hash': game_data['img_logo_url'],
                    })

                ext.flask_redis.set(cache_key, msgpack.dumps(game_datas), ex=DEFAULT_TTL)
            else:
                log.warning("Failed fetching games of %r", self)

        games = []
        for game_data in game_datas:
            games.append(SteamApp(queue_details=queue_details, **game_data))

        return games

    def to_dict(self, with_friends=True, with_games=True, with_game_details=False):
        result = {
            'avatar': self.avatar,
            'avatarfull': self.avatarfull,
            'avatarmedium': self.avatarmedium,
            'personaname': self.personaname,
            'personastate': self.personastate,
            'steamid': self.steamid,
        }
        if with_friends:
            # don't include friends of friends or games of friends
            result['friends'] = [f.to_dict(with_friends=False, with_games=False) for f in self.friends]
        if with_games:
            result['games'] = [g.to_dict(with_details=with_game_details) for g in self.games]
        return result

    @classmethod
    def get_user(cls, steamid64, queue_friends_of_friends=False):
        users = cls.get_users(
            [steamid64],
            queue_friends_of_friends=queue_friends_of_friends,
        )

        if not users:
            return None
        if len(users) > 1:
            raise Exception("More than one user found with steamid64 %s", steamid64)
        return users[0]

    @classmethod
    def get_users(cls, steamid64s, queue_friends_of_friends=False):
        users = []

        if not steamid64s:
            return users

        if isinstance(steamid64s, basestring):
            raise ValueError

        cache_key_template = cls.__name__ + ':{}'

        # fetch any users in the cache
        cached_user_keys = [cache_key_template.format(i) for i in steamid64s]

        cached_users = ext.flask_redis.mget(*cached_user_keys)
        # todo: izip didn't work for us...
        # for steamid, user_data in itertools.izip(steamid64s, cached_users):
        for user_data in cached_users:
            if not user_data:
                # user wasn't cached, we will query any cache misses with one query later
                continue
            user_data = msgpack.loads(user_data)

            if user_data:
                if 'error' in user_data and user_data['error']:
                    # we cached a missing user. dont query them again until data expires
                    steamid64s.remove(user_data['steamid'])
                else:
                    # we cached good user data
                    u = cls(queue_friends_of_friends=queue_friends_of_friends, **user_data)

                    users.append(u)

                    # don't query this user later (even if we cached empty data for them)
                    steamid64s.remove(u.steamid)

        log.debug("Retrieved users from cache: %s", users)

        if steamid64s:
            # todo: split this into multiple queries if its a lot of ids?
            # fetch any users not in the cache

            fetched_ids = []

            r = steam_api.get_json(
                "ISteamUser/GetPlayerSummaries",
                version=2,
                steamids=steamid64s,
            )
            if r:
                p = ext.flask_redis.pipeline()
                for user_data in r['response']['players']:
                    u = cls(queue_friends_of_friends=queue_friends_of_friends, **user_data)
                    users.append(u)
                    fetched_ids.append(str(u.steamid))  # this is getting annoying

                    cache_key = cache_key_template.format(u.steamid)
                    p.set(cache_key, msgpack.dumps(user_data), ex=DEFAULT_TTL)

                log.debug("Fetched users from steam: %s", fetched_ids)

                """
                if fetched_ids != steamid64s:
                    missed_ids = set(steamid64s) - set(fetched_ids)
                    log.warning("Unable to query all users. Missed: %s", missed_ids)
                    for steamid in missed_ids:
                        cache_key = cache_key_template.format(steamid)
                        p.set(
                            cache_key,
                            msgpack.dumps({
                                'steamid': steamid,
                                'error': True,
                            }),
                            ex=DEFAULT_TTL,
                        )
                """
                p.execute()

        return users

    @classmethod
    def id_from_openid(cls, claim_id):
        if not claim_id.startswith('http://steamcommunity.com/openid/id/'):
            raise ValueError("claim_id not from steamcommunity.com")
        return claim_id[len('http://steamcommunity.com/openid/id/'):]

    @classmethod
    def id_to_id64(cls, steamid):
        cache_key = cls.__name__ + ':id_to_id64:' + steamid

        result = ext.flask_redis.get(cache_key)
        if not result:
            log.info("Fetching steam64id of %s", steamid)

            r = steam_api.get_json(
                "ISteamUser/ResolveVanityURL",
                vanityurl=steamid,
            )
            if r:
                try:
                    result = r['response']['steamid']
                except (KeyError, TypeError):
                    result = None
                else:
                    ext.flask_redis.set(cache_key, result, ex=DEFAULT_TTL)

        return result


# this is an undocumented endpoint and seems to get rate limited a lot
@ext.flask_celery.task(bind=True, rate='8/s')
def get_app_details(self, appid):
    """Populate SteamApp.app_details cache."""
    raise NotImplementedError

    game_count = 0
    try:
        sa = SteamApp(appid)
        if not sa.app_details:
            raise exc.SteamApiException("No app_details for %r" % sa)
        game_count += 1
    except exc.SteamFriendsException as e:
        raise self.retry(exc=e, countdown=90 * random.randint(1, 3))

    log.info("Fetched app_details for %d games", game_count)
    return game_count


@ext.flask_celery.task(bind=True, rate='50/s')
def get_friends_of_friends(self, steamid64, with_games=False, queue_game_details=False):
    """Populate SteamUser cache."""
    raise NotImplementedError

    friend_count = 0
    game_count = 0
    try:
        su = SteamUser(steamid64, queue_friends_of_friends=False)
        for f in su.friends:
            friend_count += 1
            if with_games:
                # todo: with_game_details balloons out to WAY too many tasks
                game_count += len(f.get_games(with_details=False, queue_details=queue_game_details))

            for ff in f.friends:
                friend_count += 1
                if with_games:
                    # todo: with_game_details balloons out to WAY too many tasks
                    game_count += len(ff.get_games(with_details=False, queue_game_details=queue_game_details))
    except exc.SteamFriendsException as e:
        raise self.retry(exc=e, countdown=90 * random.randint(1, 3))

    log.info("Fetched %d friends and %d games", friend_count, game_count)
    return friend_count, game_count
