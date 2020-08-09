__cache__ = {}


def busca_preco_atual(ticker):
    if ticker in __cache__:
        return __cache__[ticker]
    else:
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
