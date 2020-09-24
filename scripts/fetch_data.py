"""
This script will fetch offers page every 8 minutes,
so users won't be affected by CX response delay.

Script will call `get_page` and will store html response to cache.
"""
import logging
import time

import sys
sys.path.insert(0, '../ofertascx')
from ofertascx import get_page
from ofertascx.cache import Cache


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_TTL = 8 * 60    # 8 minutes, less than 10
cache = Cache()


try:
    while True:
        html = get_page()
        if html:
            cache.store('html_offers', html, MAX_TTL)
        time.sleep(MAX_TTL)
except KeyboardInterrupt:
    logger.info('User interruption')
