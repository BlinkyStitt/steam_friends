from __future__ import absolute_import

import logging
import urlparse

import flask
import requests


log = logging.getLogger(__name__)


def get_json(url, version=1, **params):
    params.update({
        'format': 'json',
        'key': flask.current_app.config.get('STEAM_API_KEY'),
    })

    url = urlparse.urljoin(
        'http://api.steampowered.com/',
        '{url}/v{version}'.format(
            url=url,
            version=version,
        )
    )

    print "params:", params

    try:
        r = requests.get(url, params=params)
    except requests.exceptions.ConnectionError as e:
        log.error("%s", e)
        # todo: flash message?
        return None
    else:
        return r.json()
