import os

TESTING = os.environ.get('OCX_TESTING', False)

URL_OFFERS = 'https://cubaxchange.com/offers'

USER_AGENT = {
    'user-agent': 'ofertascx/bot contact:@n3s7or'
}

CACHE_CONN = ('localhost', 11211) if TESTING else (os.environ.get('CACHE_HOST'), os.environ.get('CACHE_PORT'))

BOT_TOKEN = os.environ.get('BOT_TOKEN')
DEVELOPER_CHAT_ID = os.environ.get('DEVELOPER_CHAT_ID')
