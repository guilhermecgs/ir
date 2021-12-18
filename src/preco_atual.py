from cachier import cachier
import datetime

from src.crawler_yahoo import busca_preco_atual_yahoo as preco_atual_yahoo
from src.utils import CACHE_DIR
from src.crawler_advfn import advfn_preco_atual

@cachier(stale_after=datetime.timedelta(hours=3), cache_dir=CACHE_DIR)
def busca_preco_atual(ticker):

    try:
        preco_atual = preco_atual_yahoo(ticker)

        if preco_atual is not None:
            return preco_atual
    except:
        pass

    try:
        preco_atual = advfn_preco_atual(ticker)

        if preco_atual is not None:
            return preco_atual
    except:
        pass

    return None