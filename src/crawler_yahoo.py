from cachier import cachier
import datetime

from src.utils import CACHE_DIR


@cachier(stale_after=datetime.timedelta(hours=3), cache_dir=CACHE_DIR)
def busca_preco_atual(ticker):
    preco = __third_party_lib(ticker)
    if type(preco) is float:
        return preco
    else:
        return None


def __third_party_lib(ticker):
    from requests import sessions
    session = sessions.Session()
    ticker_sa = ticker + '.sa'

    try:
        from yahooquery import Ticker
        ticker = Ticker(ticker_sa, validate=True, status_forcelist=[404], backoff_factor=5,
                       retry=10, progress=True, session=session)
        preco = ticker.price[ticker_sa]['regularMarketPrice']
    finally:
        session.close()
    return preco
