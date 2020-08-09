import sys
from urllib.request import Request, urlopen


this = sys.modules[__name__]
this.__cache__ = {}


def __get_url(ticker):
    return 'https://opcoes.net.br/{ticker}'.format(ticker=ticker)


def eh_tipo_opcao(ticker):
    ticker = ticker.lower()

    if ticker in this.__cache__:
        return this.__cache__[ticker]['eh_tipo_opcao']
    else:
        try:
            this.__cache__[ticker] = __recupera_informacoes(ticker)

            return this.__cache__[ticker]['eh_tipo_opcao']

        except Exception as ex:
            return None


def __recupera_informacoes(ticker):
    if __eh_opcao(ticker):
        return {'eh_tipo_opcao': True}
    else:
        return {'eh_tipo_opcao': False}


def __eh_opcao(ticker):
    ticker = ticker.upper()

    try:
        # Making the website believe that you are accessing it using a Mozilla browser
        req = Request(__get_url(ticker), headers={'User-Agent': 'Mozilla/5.0'})
        result = urlopen(req)

        if result.status == 200:
            return True
        else:
            return False
    except Exception as ex:
        return False
