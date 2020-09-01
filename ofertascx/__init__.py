import sys
import requests
from ofertascx import settings
from ofertascx.parser import process_table
from ofertascx.cache import Cache


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


def get_page() -> str or bool:
    """Fetch cubaxchange public offers page"""
    r = None
    try:
        r = requests.get(settings.URL_OFFERS, headers=settings.USER_AGENT)
    except Exception as e:
        print(e)
        return False

    if r and r.status_code == requests.codes.ok:
        return r.text
    raise 'Something bad happen while fetching the page: %s' % r.reason


def scrape_offers():
    cache = Cache()
    html = get_page()

    if not html:
        raise Exception('Could not fetch offers page')

    for offer in Offers:
        cache.store(offer, list(process_table(selector=offer, page=html)))


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
    for _filter in kwargs:
        if _filter not in FILTER_TYPE:
            kwargs.pop(_filter)

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


def filter_ventas(**kwargs):
    """Shortcut for filter_offers"""
    return filter_offers(get_ventas(), **kwargs)


def filter_compras(**kwargs):
    """Shortcut for filter_compras"""
    return filter_offers(get_compras(), **kwargs)
