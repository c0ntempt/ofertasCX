import os
from emoji import emojize


TESTING = bool(os.environ.get('OCX_TESTING', False))
CACHE_CONN = ('localhost', 11211) if TESTING else (os.environ.get('CACHE_HOST'), int(os.environ.get('CACHE_PORT')))
BOT_TOKEN = os.environ.get('BOT_TOKEN')
DEVELOPER_CHAT_ID = os.environ.get('DEVELOPER_CHAT_ID')

URL_BASE = 'https://heavenex.com'
URL_PUBLIC = URL_BASE + '/public'
URL_OFFERS = URL_BASE + '/offers'
MY_REFERRAL = 'https://www.heavenex.com/register-by-url/4aa1a852-f294-49ca-88b1-e00d7ab3636f'

USER_AGENT = {
    'user-agent': 'ofertashx/bot contact: https://t.me/n3s7or'
}


# Emojis
EMOJI_OK = emojize(':white_check_mark:', use_aliases=True)
EMOJI_KO = emojize(':x:', use_aliases=True)
EMOJI_THUMBS_UP = emojize(':+1:', use_aliases=True)
EMOJI_THUMBS_DOWN = emojize(':-1:', use_aliases=True)