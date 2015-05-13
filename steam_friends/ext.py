from flask.ext import cache, openid


# todo: use a real cache
cache = cache.Cache(config={'CACHE_TYPE': 'simple'})

oid = openid.OpenID(safe_roots=[])
