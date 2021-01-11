from cachier import cachier
import datetime


@cachier(stale_after=datetime.timedelta(hours=2))
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
        preco = Ticker(ticker_sa, session=session).price[ticker_sa]['regularMarketPrice']
    finally:
        session.close()
    return preco
