from __future__ import absolute_import

import functools
import logging
import random

import requests
import steam.api

from steam_friends import exc, ext


log = logging.getLogger(__name__)


@functools.total_ordering
class SteamApp(object):

    image_url = "http://media.steampowered.com/steamcommunity/public/images/apps/{appid}/{hash}.jpg"

    # eventhough this says "appids", it returns null when given multiple values
    details_url = "http://store.steampowered.com/api/appdetails/?appids={appid}"

    # these appids don't seem to have store pages but are still returned in games lists...
    # todo: figure out what all these actually are if they aren't games
    skipped_appids = (
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

        # these are actually just hashes and not full urls
        # setting them sets the cache. setting them to None queries the cache
        self.img_logo_hash = kwargs.pop('img_logo_url', None)
        self.img_icon_hash = kwargs.pop('img_icon_url', None)

        if queue_details:
            try:
                # pre-emptively fill caches
                # task_id = get_app_details.delay(self.steamid)  # this should work, but it misses our config :'(
                task_id = ext.flask_celery.get_task('get_app_details').delay(self.appid)
                log.debug("queued get_app_details: %s", task_id)
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

    # todo: cache result in flask.g
    @property
    def app_details(self):
        # cache memoize doesn't work well for us here because we dont want to cache api failures

        if self.appid in self.skipped_appids:
            return

        cache_key = self.app_details_key
        cached_app_details = ext.cache.cache.get(cache_key)
        if not cached_app_details:

            # fetch any users not in the cache
            details_url = self.details_url.format(
                appid=self.appid,
            )
            r = requests.get(details_url)

            try:
                app_json = r.json()[str(self.appid)]
            except (TypeError, KeyError):
                app_json = None

            # sometimes we get back "null" sometimes "success == failed"
            if not app_json or 'success' not in app_json or not app_json['success']:
                log.warning("Failed querying %s: %s", details_url, r.text)
                return

            cached_app_details = app_json['data']
            ext.cache.cache.set(cache_key, cached_app_details)

        return cached_app_details

    @property
    def img_icon_hash_key(self):
        return "{!r}:img_icon_hash".format(self, self.appid)

    @property
    def img_icon_hash(self):
        if self._img_icon_hash is None:
            self._img_icon_hash = ext.cache.cache.get(self.img_icon_hash_key)
        return self._img_icon_hash

    @img_icon_hash.setter
    def img_icon_hash(self, value):
        if value is not None:
            ext.cache.cache.set(self.img_icon_hash_key, value)
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
            self._img_logo_hash = ext.cache.cache.get(self.img_logo_hash_key)
        return self._img_logo_hash

    @img_logo_hash.setter
    def img_logo_hash(self, value):
        if value is not None:
            ext.cache.cache.set(self.img_logo_hash_key, value)
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

        # todo: how should we actually handle encoding?
        self._name = value.encode('ascii', 'ignore')

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
        self.steamid = steamid  # should this really be named steamid64

        self.avatar = kwargs.pop('avatar', None)
        self.avatarmedium = kwargs.pop('avatarmedium', None)
        self.avatarfull = kwargs.pop('avatarfull', None)
        self.personaname = kwargs.pop('personaname', '').encode('ascii', 'ignore')  # todo: improve this
        self.personastate = kwargs.pop('personastate', None)

        if queue_friends_of_friends:
            try:
                # pre-emptively fill caches
                # task_id = get_friends_of_friends.delay(self.steamid)  # this should work, but it misses our config
                task_id = ext.flask_celery.get_task('get_friends_of_friends').delay(self.steamid)
                log.debug("queued get_friends_of_friends(%r): %s", self, task_id)
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
    @ext.cache.memoize()
    def friends(self, queue_friends_of_friends=False, relationship='friend'):
        # todo: this is a property, but it has kwargs...
        f = []

        # todo: only lookup friends that aren't in our cache
        log.info("Fetching friends of %r", self)
        friends_response = steam.api.interface('ISteamUser').GetFriendList(
            steamid=self.steamid,
            relationship=relationship,
        )
        try:
            for friends_data in friends_response['friendslist']['friends']:
                f.append(friends_data['steamid'])
        except steam.api.HTTPError:
            log.warning("Failed fetching friends of %r", self)
        return self.get_users(f, queue_friends_of_friends=queue_friends_of_friends)

    @property
    @ext.cache.memoize()
    def games(self, include_appinfo=1, include_played_free_games=1, queue_details=1):
        # todo: this is a property, but it has kwargs...
        g = []

        log.info("Fetching games of %r", self)
        games_response = steam.api.interface('IPlayerService').GetOwnedGames(
            steamid=self.steamid,
            include_appinfo=include_appinfo,
            include_played_free_games=include_played_free_games,
        )
        if games_response['response'] == {}:
            log.warning("Failed fetching games of %r", self)
        else:
            for game_data in games_response['response']['games']:
                # todo: sometimes string, sometimes int...
                if str(game_data['appid']) in SteamApp.skipped_appids:
                    continue
                g.append(SteamApp(queue_details=queue_details, **game_data))
        return g

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

        cache_key_template = cls.__name__ + ':{}'

        # fetch any users in the cache
        cached_user_keys = [cache_key_template.format(i) for i in steamid64s]
        cached_users = ext.cache.cache.get_dict(*cached_user_keys)
        for cached_data in cached_users.itervalues():
            if not cached_data:
                # this shouldn't ever happen
                continue

            u = cls(**cached_data)

            steamid64s.remove(u.steamid)
            users.append(u)
        log.debug("Retrieved from cache: %s", users)

        if steamid64s:
            # fetch any users not in the cache
            users_response = steam.api.interface('ISteamUser').GetPlayerSummaries(
                steamids=steamid64s,
                version=2,
            )
            for user_data in users_response['response']['players']:
                if not user_data:
                    # this shouldn't ever happen
                    continue
                u = cls(queue_friends_of_friends=queue_friends_of_friends, **user_data)

                cache_key = cache_key_template.format(u.steamid)

                ext.cache.cache.set(cache_key, user_data)  # never cache objects
                users.append(u)
            log.debug("Fetched from steam: %s", steamid64s)

        return users

    @classmethod
    def id_from_openid(cls, claim_id):
        if not claim_id.startswith('http://steamcommunity.com/openid/id/'):
            raise ValueError("claim_id not from steamcommunity.com")
        return claim_id[len('http://steamcommunity.com/openid/id/'):]

    @classmethod
    @ext.cache.memoize()
    def id_to_id64(cls, steamid):
        # todo: cache this
        log.info("Checking for steam64id of %s", steamid)
        r = steam.api.interface('ISteamUser').ResolveVanityURL(vanityurl=steamid)
        try:
            return r['response']['steamid']
        except (KeyError, steam.api.HTTPError):
            return None


# this is an undocumented endpoint and seems to get rate limited a lot
@ext.flask_celery.task(bind=True, rate='8/s')
def get_app_details(self, appid):
    """Populate SteamApp.app_details cache."""
    game_count = 0
    try:
        sa = SteamApp(appid)
        if not sa.app_details:
            raise exc.SteamApiException("No app_details for %r" % sa)
        game_count += 1
    except exc.SteamFriendsException as e:
        raise self.retry(exc=e, countdown=90 * random.randint(1, 3))

    log.info("Queued fetch of %d games", game_count)
    return game_count


@ext.flask_celery.task(bind=True, rate='50/s')
def get_friends_of_friends(self, steamid64, with_games=False):
    """Populate SteamUser cache."""
    friend_count = 0
    game_count = 0
    try:
        su = SteamUser(steamid64, queue_friends_of_friends=False)
        for f in su.friends:
            friend_count += 1
            if with_games:
                game_count += len(f.games)

            for ff in f.friends:
                friend_count += 1
                if False and with_games:
                    # todo: this balloons out to WAY too many tasks
                    game_count += len(ff.games)
    except exc.SteamFriendsException as e:
        raise self.retry(exc=e, countdown=90 * random.randint(1, 3))

    log.info("Queued fetch of %d friends and %d games", friend_count, game_count)
    return friend_count, game_count
