from cachier import cachier
import datetime

from src.utils import CACHE_DIR


@cachier(stale_after=datetime.timedelta(hours=3), cache_dir=CACHE_DIR)
def busca_preco_atual_yahoo(ticker):
    preco_option_b = __third_party_lib_option_b(ticker)
    if type(preco_option_b) is float:
        return preco_option_b
    else:
        preco_option_a = __third_party_lib_option_a(ticker)
        if type(preco_option_a) is float:
            return preco_option_a

    return None


def __ticker_sa(ticker):
    ticker_sa = ticker + '.sa'.upper()
    return ticker_sa


def __third_party_lib_option_a(ticker):
    from requests import sessions
    session = sessions.Session()
    ticker_sa = __ticker_sa(ticker)

    try:
        from yahooquery import Ticker
        ticker = Ticker(ticker_sa, validate=True, status_forcelist=[404], backoff_factor=5,
                        retry=10, progress=True, session=session)
        preco = ticker.price[ticker_sa]['regularMarketPrice']
    except Exception as ex:
        return None
    finally:
        session.close()
    return preco


def __third_party_lib_option_b(ticker):
    import yfinance as yf

    try:
        ticker = yf.Ticker(__ticker_sa(ticker))
        return ticker.info['currentPrice']
    except Exception as ex:
        return None
