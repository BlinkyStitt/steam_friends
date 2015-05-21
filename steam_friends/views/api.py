import flask

from steam_friends import models


blueprint = flask.Blueprint('api', __name__)


@blueprint.route('/steam_user/<steamid64>', methods=['GET'])
def steam_user(steamid64):
    if not steamid64.isnumeric():
        steamid64 = models.SteamUser.id_to_id64(steamid64)

    su = models.SteamUser.get_user(steamid64)
    if su is None:
        return flask.jsonify({}), 404
    return flask.jsonify(su.to_dict())
