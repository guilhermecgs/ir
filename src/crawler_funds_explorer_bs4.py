import sys
import ssl
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, Tag

# For ignoring SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


this = sys.modules[__name__]
this.__cache__ = {}


def eh_tipo_fii(ticker):

    ticker_corrigido = __corrige_ticker(ticker)

    if ticker_corrigido in this.__cache__:
        return this.__cache__[ticker_corrigido]['eh_tipo_fii']
    else:
        this.__cache__[ticker_corrigido] = __recupera_informacoes(ticker_corrigido)
        return this.__cache__[ticker_corrigido]['eh_tipo_fii']


def fii_dividend_yield(ticker):

    ticker_corrigido = __corrige_ticker(ticker)

    if ticker_corrigido in this.__cache__:
        return this.__cache__[ticker_corrigido]['dividend_yield']
    else:
        this.__cache__[ticker_corrigido] = __recupera_informacoes(ticker_corrigido)
        return this.__cache__[ticker_corrigido]['dividend_yield']


def __corrige_ticker(ticker):
    ticker_corrigido = ticker
    if ticker.endswith('12'):
        ticker_corrigido = ticker.replace('12', '11')
    return ticker_corrigido


def __recupera_informacoes(ticker_corrigido):
    try:
        url = "https://www.fundsexplorer.com.br/funds/%s" % (ticker_corrigido)

        # Making the website believe that you are accessing it using a Mozilla browser
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()

        soup = BeautifulSoup(webpage, 'html.parser')
        # html = soup.prettify('utf-8')

        return {'eh_tipo_fii': __obtem_tipo(soup), 'dividend_yield': __obtem_dividend_yield(soup)}
    except:
        return {'eh_tipo_fii': False, 'dividend_yield': None}


def __obtem_tipo(soup):
    try:
        titles = soup.findAll('h1', attrs={'class': 'section-title'})
        if len(titles):
            return True
        else:
            return False
    except:
        return False


def __obtem_dividend_yield(soup):
    try:
        span = soup.findAll('span', string='Dividend Yield')

        if len(span):
            span = span[0]

            for element in span.parent.descendants:
                if isinstance(element, Tag) \
                        and 'class' in element.attrs \
                        and 'indicator-value' in element.attrs['class']:
                    yield_string = element.text
                    return float(yield_string.replace(' ', '').replace('%', '')
                                 .replace('\n', '').replace('.', '').replace(',', '.'))
        return None
    except Exception as ex:
        return None

