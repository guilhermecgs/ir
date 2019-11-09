import ssl
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

# For ignoring SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def e_tipo_etf(ticker: str):
    try:
        ticker_caps = ticker.upper()
        url = 'https://br.investing.com/etfs/brazil-etfs'

        # Making the website believe that you are accessing it using a Mozilla browser
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()

        soup = BeautifulSoup(webpage, 'html.parser')
        # html = soup.prettify('utf-8')

        for td in soup.findAll('td', attrs={'title': ticker_caps}):
            return True

        return False
    except Exception as ex:
        return False