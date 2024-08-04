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


def __corrige_ticker(ticker):
    ticker_corrigido = ticker
    if ticker.endswith('12'):
        ticker_corrigido = ticker.replace('12', '11')
    return ticker_corrigido.upper()


@cachier(stale_after=datetime.timedelta(hours=3), cache_dir=CACHE_DIR)
def busca_preco_atual_brapi(ticker):
    ticker_corrigido = __corrige_ticker(ticker)
    try:
        url = "https://brapi.dev/quote/%s" % (ticker_corrigido)
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()

        soup = BeautifulSoup(webpage, 'html.parser')

        # Find the parent div containing both spans
        price_container = soup.find('span', text='Preço').find_parent('div')

        # Find the span with the price within the same parent div
        price_element = price_container.find('span', class_='text-2xl font-bold')
        price = price_element.text.strip()

        # Clean up the price text
        price = price.replace('R$', '').replace('$', '').replace(',', '.').replace('\xa0', '').strip()
        try:
            price_float = float(price)
            return price_float
        except ValueError:
            return None
    except:
        return None
