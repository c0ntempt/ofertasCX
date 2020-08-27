from pymemcache.client.base import Client
from pymemcache import serde
from ofertascx.settings import CACHE_CONN

TTL = 60 * 10  # Stored values 10 minutes


class Cache:
    class __Cache:
        def __init__(self):
            self.client = Client(CACHE_CONN, serde=serde.pickle_serde)

    instance = None

    def store(self, key, value, expire=TTL):
        if not Cache.instance:
            Cache.instance = Cache.__Cache()
        self.instance.client.set(key, value=value, expire=expire)

    def restore(self, key):
        if not Cache.instance:
            Cache.instance = Cache.__Cache()
        return self.instance.client.get(key)
