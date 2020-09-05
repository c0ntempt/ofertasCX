import os
from enum import Enum


TESTING = bool(os.environ.get('OCX_TESTING', False))
CACHE_CONN = ('localhost', 11211) if TESTING else (os.environ.get('CACHE_HOST'), int(os.environ.get('CACHE_PORT')))
BOT_TOKEN = os.environ.get('BOT_TOKEN')
DEVELOPER_CHAT_ID = os.environ.get('DEVELOPER_CHAT_ID')

URL_BASE = 'https://cubaxchange.com'
URL_PUBLIC = URL_BASE + '/public'
URL_OFFERS = URL_BASE + '/offers'
MY_REFERRAL = 'https://bit.ly/2ZtAyrq'

USER_AGENT = {
    'user-agent': 'ofertascx/bot contact: https://t.me/n3s7or'
}


class PagoIntervals(Enum):
    MIN = {'max': 5}
    MID = {'min': 5, 'max': 15}
    MAX = {'min': 15}

    def __str__(self):
        return self.name
