import ssl
import time
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

# For ignoring SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

__cache__ = {}


def busca_preco_atual(ticker):
    if ticker in __cache__:
        return __cache__[ticker]
    try:
        ticker_sa = ticker + '.SA'
        url = "http://finance.yahoo.com/quote/%s?p=%s" % (ticker_sa, ticker_sa)

        # Making the website believe that you are accessing it using a Mozilla browser
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()

        time.sleep(0.3)

        soup = BeautifulSoup(webpage, 'html.parser')
        # html = soup.prettify('utf-8')

        def extract_price_from_span(span):
            preco_atual = float(span.text.replace(',', '').strip())

            return preco_atual

        for span in soup.findAll('span', attrs={'class': 'Trsdu(0.3s) Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(b)'}):
            preco_atual = extract_price_from_span(span)
            __cache__[ticker] = preco_atual
            return preco_atual

        for span in soup.findAll("span", {"data-reactid": "32"}):
            preco_atual = extract_price_from_span(span)
            __cache__[ticker] = preco_atual
            return preco_atual

        raise Exception('Preco ticker nao encontrado ' + ticker)
    except Exception as ex:
        raise Exception('Preco ticker nao encontrado ' + ticker, ex)