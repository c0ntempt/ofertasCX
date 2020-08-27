import requests
from ofertascx import settings
from ofertascx.parser import process_table
from ofertascx.cache import Cache


def get_page() -> str or bool:
    """Fetch cubaxchange public offers page"""

    # Perhaps this isn't the best approach
    if settings.TESTING:
        with open(__path__[0] + '/tests/offers.html', 'r') as f:
            return f.read()

    r = None
    try:
        r = requests.get(settings.URL_OFFERS, headers=settings.USER_AGENT)
    except Exception as e:
        print(e)
        return False

    if r and r.status_code == requests.codes.ok:
        return r.text
    raise 'Something bad happen while fetching the page: %s' % r.reason


# TODO Avoid code duplication
def get_ventas():
    cache = Cache()
    ventas = cache.restore('ventas')
    if ventas:
        return ventas
    ventas = list(process_table(selector='ventas', page=get_page()))
    cache.store('ventas', ventas)
    return ventas


def get_compras():
    cache = Cache()
    compras = cache.restore('compras')
    if compras:
        return compras
    compras = list(process_table(selector='compras', page=get_page()))
    cache.store('compras', compras)
    return compras
