from enum import Enum

from src.crawler_yahoo_bs4 import busca_preco_atual
from src.crawler_b3_etfs import e_tipo_etf
from src.crawler_funds_explorer_bs4 import e_tipo_fii

__cache__ = {}

class TipoTicker(Enum):
    ETF = 1
    FII = 2
    ACAO = 3


def tipo_ticker(ticker):
    if ticker in __cache__:
        return __cache__[ticker]
    else:
        if e_tipo_fii(ticker):
            __cache__[ticker] = TipoTicker.FII
            return TipoTicker.FII

        if e_tipo_etf(ticker):
            __cache__[ticker] = TipoTicker.ETF
            return TipoTicker.ETF

        try:
            busca_preco_atual(ticker)
            __cache__[ticker] = TipoTicker.ACAO
            return TipoTicker.ACAO
        except:
            pass

        return None