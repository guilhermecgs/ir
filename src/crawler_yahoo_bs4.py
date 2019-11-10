import ssl
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

# For ignoring SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def busca_preco_atual(ticker):
    try:
        ticker_sa = ticker + '.SA'
        url = "http://finance.yahoo.com/quote/%s?p=%s" % (ticker_sa, ticker_sa)

        # Making the website believe that you are accessing it using a Mozilla browser
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()

        soup = BeautifulSoup(webpage, 'html.parser')
        # html = soup.prettify('utf-8')

        for span in soup.findAll('span', attrs={'class': 'Trsdu(0.3s) Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(b)'}):
            return float(span.text.replace(',', '').strip())

        raise Exception('Preco ticker nao encontrado ' + ticker)
    except Exception as ex:
        raise Exception('Preco ticker nao encontrado ' + ticker, ex)