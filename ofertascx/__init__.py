import requests
from ofertascx import settings
from ofertascx.parser import process_table
from ofertascx.cache import Cache


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
