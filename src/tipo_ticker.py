from enum import Enum

from src.crawler_yahoo import busca_preco_atual
from src.crawler_b3_etfs import e_tipo_etf
from src.crawler_funds_explorer_bs4 import eh_tipo_fii
from src.dados import ticker_tipo

from cachier import cachier
import datetime


class TipoTicker(Enum):
    ETF = 1
    FII = 2
    ACAO = 3
    OPCAO = 4
    FUTURO = 5
    FIP = 6
    FIPIE = 7
    BDR = 8

@cachier(stale_after=datetime.timedelta(days=30))
def tipo_ticker(ticker):
    tp = ticker_tipo(ticker)
    if tp:
        if tp == 'FII':
            return TipoTicker.FII
        if tp == 'FIPIE':
            return TipoTicker.FIPIE
        if tp == 'FIP':
            return TipoTicker.FIP
        if tp == 'BDR':
            return TipoTicker.BDR
        if tp == 'ETF':
            return TipoTicker.ETF
        if tp == 'ACAO':
            return TipoTicker.ACAO
            
    if eh_tipo_fii(ticker):
        return TipoTicker.FII

    if e_tipo_etf(ticker):
        return TipoTicker.ETF

    try:
        busca_preco_atual(ticker)
        return TipoTicker.ACAO
    except:
        pass

    from src.crawler_advfn import CrawlerAdvfn
    crawler_advfn = CrawlerAdvfn()

    if crawler_advfn.busca_tipo_ticker(ticker) == TipoTicker.ACAO:
        return TipoTicker.ACAO

    if crawler_advfn.busca_tipo_ticker(ticker) == TipoTicker.OPCAO:
        return TipoTicker.OPCAO

    if crawler_advfn.busca_tipo_ticker(ticker) == TipoTicker.FUTURO:
        return TipoTicker.FUTURO

    return None
