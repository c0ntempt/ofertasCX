import logging
import sys
import time
from enum import Enum

import requests
from ofertascx import settings
from ofertascx.parser import process_table, process_public_profile
from ofertascx.cache import Cache
from ofertascx.settings import URL_PUBLIC

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


FILTER_TYPE = ('cripto', 'valor', 'pago')


# TODO Organize this
class OfferType(dict):
    COMPRA = 'compras'
    VENTA = 'ventas'

    def __init__(self):
        super().__init__()
        self[self.COMPRA] = self.COMPRA
        self[self.VENTA] = self.VENTA

    def __getattr__(self, item):
        if item in self:
            return self[item]
        return None


Offers = OfferType()


def delay_check(start, info, threshold=1.5):
    stop = time.time()
    delay = stop - start
    if delay > threshold:
        logger.warning('Slow function detected: %s seconds in %s', delay, info)


def get_page(url) -> str or bool:
    """Fetch cubaxchange public offers page"""
    start = time.time()
    try:
        r = requests.get(url, headers=settings.USER_AGENT, allow_redirects=False)
    except Exception as e:
        logger.error(e)
        return False
    finally:
        delay_check(start, get_page.__name__)

    if r and r.status_code == requests.codes.ok:
        return r.text

    # TODO Improve this, this is not scalable
    if r.status_code == requests.codes.found:
        return ''
    raise Exception('Something bad happen while fetching the page: (%s, %s, %s)' % (url, r.status_code, r.reason))


def scrape_offers():
    cache = Cache()
    html = get_page(settings.URL_OFFERS)

    if not html:
        raise Exception('Could not fetch offers page')

    for offer in Offers:
        cache.store(offer, list(process_table(selector=offer, page=html)))


def scrape_user_profile(user_url: str):
    # TODO Implement cache
    html = get_page(user_url)
    if not html:
        return ''
    return process_public_profile(html)


def get_offer(type_=Offers.VENTA):
    if type_ not in Offers:
        raise Exception('Non existent type')

    cache = Cache()

    offer = cache.restore(type_)
    if offer:
        return offer
    else:
        scrape_offers()

    return cache.restore(type_)


def get_ventas():
    """Shortcut for get_offer"""
    return get_offer(type_=Offers.VENTA)


def get_compras():
    """Shortcut for get_offer"""
    return get_offer(type_=Offers.COMPRA)


def filter_offers(offers, **kwargs):
    # I dont like this
    for key, value in list(kwargs.items()):
        if key not in FILTER_TYPE:
            kwargs.pop(key)
        if isinstance(value, Enum):
            kwargs[key] = value.value

    _offers = []

    for offer in offers:
        match = True
        for _filter, value in kwargs.items():
            # Ugly as hell
            if isinstance(value, (str, list)):
                if value not in offer[_filter]:
                    match = False
                    break
            elif isinstance(value, dict) and _filter == FILTER_TYPE[1]:
                _max = kwargs[_filter].get('max', sys.maxsize)
                _min = kwargs[_filter].get('min', -sys.maxsize)

                if not (_min < offer[_filter] <= _max):
                    match = False
                    break

        if match:
            _offers.append(offer)

    return _offers


def gen_key(**kwargs):
    return '-'.join([('%s(%s)' % (i[0], i[1])).replace(' ', '') for i in sorted(kwargs.items())])


def gen_user_profile_link(user):
    return '{0}/{1}'.format(URL_PUBLIC, user)


def filter_ventas(**kwargs):
    """Shortcut for filter_offers with cache"""

    cache = Cache()
    key = 'ventas/%s' % gen_key(**kwargs)

    offers = cache.restore(key)
    if offers:
        return offers

    offers = filter_offers(get_ventas(), **kwargs)
    cache.store(key, offers)
    return offers


def filter_compras(**kwargs):
    """Shortcut for filter_compras with cache"""

    cache = Cache()
    key = 'compras/%s/' % gen_key(**kwargs)

    offers = cache.restore(key)
    if offers:
        return offers

    offers = filter_offers(get_compras(), **kwargs)
    cache.store(key, offers)
    return offers


# TODO perhaps implement cache
def get_payment_types(filter) -> list:
    if filter.get('offer', None) == Offers.VENTA:
        filter_method = filter_ventas
    elif filter.get('offer', None) == Offers.COMPRA:
        filter_method = filter_compras
    else:
        raise Exception('Impossible')

    if filter.get('cripto', None):
        offers = filter_method(cripto=filter.get('cripto'))
    else:
        offers = filter_method()

    payment_types = []
    for offer in offers:
        for ptype in offer['pago']:
            if ptype not in payment_types:
                payment_types.append(ptype)

    return payment_types
