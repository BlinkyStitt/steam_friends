from flask.ext import cache, openid


cache = cache.Cache()
oid = openid.OpenID(safe_roots=[])
