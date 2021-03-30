from bs4 import BeautifulSoup
from datetime import datetime
import re

from ofertascx.settings import EMOJI_OK, EMOJI_KO


def process_table(selector: str, page: str) -> iter:
    html = BeautifulSoup(page, 'html.parser')
    table = html.find(name='div', attrs={'id': selector}).table
    timestamp = datetime.now()

    for offer in table.tbody.find_all('tr'):
        data = offer.find_all('td')
        yield dict(
            usuario=data[1].text.strip(),
            link=data[1].a.get('href'),
            avatar=data[1].a.img.get('src'),
            kyc=True if 'fa-check-circle' in data[2].span.get('class') else False,
            cripto=data[3].text.strip(),
            # intervalo=[float(i.replace(',', '.')) for i in data[4].text.strip().split('\n')[0].split('-')],
            valor=int(data[5].text.strip().split('\n')[0].replace('%', '')),
            pago=[i.strip() for i in data[6].text.strip().split('\n') if not i.isspace()],
            timestamp=timestamp
        )


def process_public_profile(page: str) -> dict:
    all_data = BeautifulSoup(page, 'html.parser').find(name='div', attrs={'class': 'main', 'role': 'main'}) \
        .find_all(attrs={'class': 'card-body'})

    # Datos principales
    pattern = re.compile(r'Nombre de Usuario:\s+(?P<username>.*)' \
                         'Última vez en el sitio:.*Votos de confianza: (?P<trust>\d+)' \
                         ' Usuarios que lo ignoran: (?P<distrust>\d+)')

    profile = all_data[0].find_all(attrs={'class': 'col-md-6'})[1]  #.text.strip().replace('\n', ' ')

    # Contains username, trust and distrust
    data = pattern.match(profile.text.strip().replace('\n', ' '))
    if data:
        data = {k: v.strip() for k, v in data.groupdict().items()}
        if 'fa-check-circle' in profile.span.attrs['class']:
            kyc = EMOJI_OK
        elif 'fa-window-close' in profile.span.attrs['class']:
            kyc = EMOJI_KO
        else:
            kyc = '?'
        data.update({'kyc': kyc})

    return data
