import ssl
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

# For ignoring SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def e_tipo_fii(ticker):
    try:
        url = "https://www.fundsexplorer.com.br/funds/%s" % (ticker)

        # Making the website believe that you are accessing it using a Mozilla browser
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()

        soup = BeautifulSoup(webpage, 'html.parser')
        # html = soup.prettify('utf-8')

        titles = soup.findAll('h1', attrs={'class': 'section-title'})
        if len(titles):
            return True
        else:
            return False
    except:
        return False