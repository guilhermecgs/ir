import sys
import ssl
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, Tag

from cachier import cachier
import datetime
import re

# For ignoring SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


this = sys.modules[__name__]


def eh_tipo_fii(ticker):
    return __pega_parametro(ticker,'eh_tipo_fii')


def fii_dividend_yield(ticker):
    return __pega_parametro(ticker,'dividend_yield')


def fii_p_vp(ticker):
    return __pega_parametro(ticker,'p_vp')

def fii_nome(ticker):
    return __pega_parametro(ticker,'nome')

def fii_razao_social(ticker):
    return __pega_parametro(ticker,'razao_social')

def fii_cnpj(ticker):
    return __pega_parametro(ticker,'cnpj')


def __pega_parametro(ticker, parametro):

    ticker_corrigido = __corrige_ticker(ticker)

    return __recupera_informacoes(ticker_corrigido)[parametro]


def __corrige_ticker(ticker):
    ticker_corrigido = re.sub("1[234]$","11", ticker)
    return ticker_corrigido

@cachier(stale_after=datetime.timedelta(days=1))
def __recupera_informacoes(ticker_corrigido):
    try:
        url = "https://www.fundsexplorer.com.br/funds/%s" % (ticker_corrigido)

        # Making the website believe that you are accessing it using a Mozilla browser
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()

        soup = BeautifulSoup(webpage, 'html.parser')
        # html = soup.prettify('utf-8')

        return {'eh_tipo_fii': __obtem_tipo(soup), 
            'dividend_yield': __obtem_valor(soup, 'Dividend Yield'), 
            'p_vp' : __obtem_valor(soup, 'P/VP'), 
            'razao_social' : __obtem_dados(soup, 'Razão Social'),
            'cnpj' : __obtem_dados(soup, 'CNPJ'),
            'nome' : __obtem_nome(soup) }
    except:
        return {'eh_tipo_fii': False, 'dividend_yield': None, 'p_vp' : None, 'razao_social' : None, 'cnpj' : None, 'nome' : None }


def __obtem_nome(soup):
    try:
        titles = soup.findAll('h3', attrs={'class': 'section-subtitle'})
        if len(titles):
            return titles[0].text
        else:
            return None
    except:
        return None


def __obtem_tipo(soup):
    try:
        titles = soup.findAll('h1', attrs={'class': 'section-title'})
        if len(titles):
            return True
        else:
            return False
    except:
        return False


def __obtem_valor(soup, titulo):
    try:
        span = soup.findAll('span', string=titulo)

        if len(span):
            span = span[0]

            for element in span.parent.descendants:
                if isinstance(element, Tag) \
                        and 'class' in element.attrs \
                        and 'indicator-value' in element.attrs['class']:
                    value_string = element.text
                    return float(value_string.replace(' ', '').replace('%', '')
                                 .replace('\n', '').replace('.', '').replace(',', '.'))
        return None
    except Exception as ex:
        return None

def __obtem_dados(soup, titulo):
    try:
        span = soup.findAll('span', string=titulo)

        if len(span):
            span = span[0]
            for element in span.parent.descendants:
                if isinstance(element, Tag) \
                        and 'class' in element.attrs \
                        and 'description' in element.attrs['class']:
                    return element.text.strip()
        return None
    except Exception as ex:
        return None

