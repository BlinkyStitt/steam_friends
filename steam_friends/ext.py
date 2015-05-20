from flask.ext import cache, openid


# todo: use a real cache
cache = cache.Cache()

oid = openid.OpenID(safe_roots=[])
