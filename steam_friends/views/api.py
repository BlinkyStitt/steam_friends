import flask

from steam_friends import models


blueprint = flask.Blueprint('api', __name__)


@blueprint.route('/steam_user/<steamid64>', methods=['GET'])
def steam_user(steamid64):
    if not steamid64.isnumeric():
        steamid64 = models.SteamUser.id_to_id64(steamid64)

    with_friends = flask.request.args.get('with_friends', '1') == '1'
    with_games = flask.request.args.get('with_games', '1') == '1'

    # this can be VERY expensive for a user with a lot of games
    # with_games_details = flask.request.args.get('with_game_details', '0') == '1'
    with_games_details = False

    su = models.SteamUser.get_user(steamid64)
    if su is None:
        return flask.jsonify({}), 404
    return flask.jsonify(su.to_dict(
        with_friends=with_friends,
        with_games=with_games,
        with_game_details=with_games_details,
    ))


@blueprint.route('/steam_app/<appid>', methods=['GET'])
def steam_app(appid):
    sa = models.SteamApp(appid=appid)
    if sa is None:
        return flask.jsonify({}), 404

    with_details = flask.request.args.get('with_details', '1') == '1'

    return flask.jsonify(sa.to_dict(
        with_details=with_details,
    ))
