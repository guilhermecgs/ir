from enum import Enum

from src.crawler_yahoo import busca_preco_atual_yahoo
from src.crawler_b3_etfs import e_tipo_etf
import src.crawler_funds_explorer_bs4 as funds_explorer
import src.crawler_fiis as fiis

from cachier import cachier
import datetime

from src.utils import CACHE_DIR


class TipoTicker(Enum):
    ETF = 1
    FII = 2
    ACAO = 3
    OPCAO = 4
    FUTURO = 5
    FIP = 6
    FIPIE = 7
    BDR = 8


@cachier(stale_after=datetime.timedelta(days=30), cache_dir=CACHE_DIR)
def tipo_ticker(ticker):

    if funds_explorer.eh_tipo_fii(ticker) or fiis.eh_tipo_fii(ticker):
        return TipoTicker.FII

    if e_tipo_etf(ticker):
        return TipoTicker.ETF

    if busca_preco_atual_yahoo(ticker):
        return TipoTicker.ACAO

    from src.crawler_advfn import advfn_tipo_ticker
    return advfn_tipo_ticker(ticker)
