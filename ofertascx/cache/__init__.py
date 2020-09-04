import logging
from pymemcache.client.base import Client
from pymemcache import serde
from ofertascx.settings import CACHE_CONN

TTL = 60 * 15  # Stored values 10 minutes


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class Cache:
    class __Cache:
        def __init__(self):
            self.client = Client(CACHE_CONN, serde=serde.pickle_serde)

    instance = None

    def store(self, key, value, expire=TTL):
        if not Cache.instance:
            Cache.instance = Cache.__Cache()

        logger.debug('caching %s = %s', key, value)
        self.instance.client.set(key, value=value, expire=expire)

    def restore(self, key):
        if not Cache.instance:
            Cache.instance = Cache.__Cache()

        value = self.instance.client.get(key)
        logger.debug('restoring %s: %s', key, value)
        return value
