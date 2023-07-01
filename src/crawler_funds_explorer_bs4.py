import ssl
from cachier import cachier
import datetime
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, Tag

# For ignoring SSL certificate errors
from src.utils import CACHE_DIR

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def eh_tipo_fii(ticker):
    ticker_corrigido = __corrige_ticker(ticker)
    return __recupera_informacoes(ticker_corrigido)['eh_tipo_fii']


def fii_dividend_yield(ticker):
    ticker_corrigido = __corrige_ticker(ticker)
    return __recupera_informacoes(ticker_corrigido)['dividend_yield']


def __corrige_ticker(ticker):
    ticker_corrigido = ticker
    if ticker.endswith('12'):
        ticker_corrigido = ticker.replace('12', '11')
    return ticker_corrigido.upper()


@cachier(stale_after=datetime.timedelta(days=3), cache_dir=CACHE_DIR)
def __recupera_informacoes(ticker_corrigido):
    try:
        url = "https://www.fundsexplorer.com.br/funds/%s" % (ticker_corrigido)
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()

        soup = BeautifulSoup(webpage, 'html.parser')
        infos = {'eh_tipo_fii': __obtem_tipo(soup), 'dividend_yield': __obtem_dividend_yield(soup)}
        return infos
    except:
        return {'eh_tipo_fii': False, 'dividend_yield': None}


def __obtem_tipo(soup):
    try:
        titles = soup.findAll('h1', attrs={'class': 'headerTicker__content__title'})
        if len(titles):
            return True
        else:
            return False
    except:
        return False


def __obtem_dividend_yield(soup):
    try:
        divs = soup.find_all('div', class_='indicators__box')

        for div in divs:
            p = div.find('p', text='DY Últ. Dividendo')
            if p:
                yield_string = div.find_next('b').text
                return float(yield_string.replace(' ', '').replace('%', '')
                                .replace('\n', '').replace('.', '').replace(',', '.'))

        return None
    except Exception as ex:
        return None

