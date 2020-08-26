import requests
from ofertascx import settings


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
