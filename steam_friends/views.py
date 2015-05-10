import collections

import flask
import steam

from steam_friends import ext, models


blueprint = flask.Blueprint('steam_friends', __name__)


@ext.oid.after_login
def after_login(resp):
    flask.session['openid'] = resp.identity_url
    steamid = models.SteamUser.id_from_openid(resp.identity_url)
    flask.g.steamid = steamid
    flask.g.steam_user = models.SteamUser.get_user(steamid)
    flask.flash('Welcome!', 'info')
    return flask.redirect(ext.oid.get_next_url())


@blueprint.route('/')
def index():
    flask.current_app.logger.debug('args: %s', flask.request.args)

    game_counter = collections.Counter()
    friend_counter = collections.Counter()

    use_default_steamid64s = True

    # we show these to the user
    passed_ids = []
    # these are what we pass to the Steam API
    steamid64s = []
    for steamid in flask.request.args.getlist('ids_and_names'):
        # even if none of the ids/names are valid, don't use the defaults
        use_default_steamid64s = False

        # assume space delimied list of ids or names
        for s in steamid.split(' '):
            s = s.strip()
            if not s:
                continue
            if s.isnumeric():  # todo: better check
                passed_ids.append(s)
                steamid64s.append(s)
            else:
                steamid64 = models.SteamUser.id_to_id64(s)
                if steamid64:
                    passed_ids.append(s)
                    steamid64s.append(steamid64)
                else:
                    flask.flash("Unable to find steamid64 for {}".format(s), "info")

    passed_ids = ' '.join(passed_ids)

    # if we were only passed names and they all failed lookup, we want to error instead of show default
    if use_default_steamid64s:
        if 'steamid' in flask.g:
            steamid64s = [
                flask.g.steamid,
            ]
            passed_ids = flask.g.steamid
        else:
            steamid64s = [
                '76561198060689354',  # ARizzo
                # '76561197980747796',  # nynjawitay
                '76561197969428769',  # Son of Themis
                # '76561197979664690',  # JC
            ]
    flask.current_app.logger.info("checking users: %r", steamid64s)

    try:
        steam_users = models.SteamUser.get_users(steamid64s)
    except steam.api.APIError as e:
        flask.current_app.logger.warning("Steam API Error for users: %s", e)
        flask.flash("Failed connecting to the steam API", "danger")
    else:
        if len(steam_users) == 0:
            flask.flash("No users found!", "danger")
        elif len(steam_users) < 2:
            flask.flash("This app works a lot better with more than 2 users.", "info")

        for u in steam_users:
            try:
                for g in u.games:
                    game_counter[g] += 1
            except steam.api.APIError as e:
                flask.current_app.logger.warning("Error while querying for games for %s: %s", u, e)
                flask.flash("Error while querying for games of %s".format(u.steamid), "danger")
                continue
            try:
                for f in u.friends:
                    flask.current_app.logger.debug("friend: %r", f)
                    friend_counter[f] += 1
            except steam.api.APIError as e:
                flask.current_app.logger.warning("Error while querying for games for %s: %s", u, e)
                flask.flash("Error while querying for friends of {}".format(u), "danger")
                continue

    return flask.render_template(
        'index.html',
        game_counter=game_counter,
        friend_counter=friend_counter,
        passed_ids=passed_ids,
        steam_users=steam_users,
    )


@blueprint.route('/login', methods=['GET', 'POST'])
@ext.oid.loginhandler
def login():
    if flask.g.steam_user is not None:
        return flask.redirect(ext.oid.get_next_url())
    if flask.request.method == 'POST':
        return ext.oid.try_login(
            'http://steamcommunity.com/openid',
            ask_for=['email', 'nickname'],
            ask_for_optional=['fullname'],
        )
    return flask.render_template(
        'login.html',
        next=ext.oid.get_next_url(),
        error=ext.oid.fetch_error(),
    )


@blueprint.route('/logout')
def logout():
    flask.session.pop('openid', None)
    flask.flash(u'You were signed out', 'info')
    return flask.redirect(ext.oid.get_next_url())


@blueprint.before_request
def lookup_current_user():
    flask.g.steam_user = None
    if 'openid' in flask.session:
        openid = flask.session['openid']
        steamid = models.SteamUser.id_from_openid(openid)
        flask.g.steamid = steamid
        flask.g.steam_user = models.SteamUser.get_user(steamid)


@ext.oid.errorhandler
def on_error(message):
    flask.flash(u'Error: ' + message)
