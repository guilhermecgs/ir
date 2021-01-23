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
    if tp in TipoTicker.__dict__:
            return TipoTicker[tp]
            
    if eh_tipo_fii(ticker):
        return TipoTicker.FII

    if e_tipo_etf(ticker):
        return TipoTicker.ETF

    try:
        busca_preco_atual(ticker)
        return TipoTicker.ACAO
    except:
        pass

    from src.crawler_advfn import advfn_tipo_ticker

    return advfn_tipo_ticker(ticker)
