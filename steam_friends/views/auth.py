import flask

from steam_friends import ext, models


blueprint = flask.Blueprint('auth', __name__)


@ext.oid.after_login
def after_login(resp):
    flask.session['openid'] = resp.identity_url
    steamid = models.SteamUser.id_from_openid(resp.identity_url)
    flask.g.steamid = steamid
    flask.g.steam_user = models.SteamUser.get_user(steamid)
    flask.flash('Welcome!', 'info')
    return flask.redirect(ext.oid.get_next_url())


@blueprint.route('/login', methods=['GET', 'POST'])
@ext.oid.loginhandler
def login():
    if flask.g.steam_user is not None:
        return flask.redirect(ext.oid.get_next_url())
    if flask.request.method == 'POST':
        return ext.oid.try_login('http://steamcommunity.com/openid')
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


@blueprint.before_app_request
def lookup_current_user():
    flask.g.steam_user = None
    if 'openid' in flask.session:
        openid = flask.session['openid']
        steamid = models.SteamUser.id_from_openid(openid)
        flask.g.steamid = steamid
        flask.g.steam_user = models.SteamUser.get_user(steamid)


@ext.oid.errorhandler
def on_error(message):
    flask.flash(u'Login Error: ' + message, 'warning')
