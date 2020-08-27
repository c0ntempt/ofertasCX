from bs4 import BeautifulSoup
from datetime import datetime


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
            intervalo=data[4].text.strip().split('\n')[0],
            valor=data[5].text.strip().split('\n')[0].replace('%', ''),
            pago=[i.strip() for i in data[6].text.strip().split('\n') if not i.isspace()],
            timestamp=timestamp
        )
