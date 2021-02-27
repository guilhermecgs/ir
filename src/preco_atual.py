from cachier import cachier
import datetime

from src.crawler_yahoo import busca_preco_atual as preco_atual_yahoo
from src.utils import CACHE_DIR


@cachier(stale_after=datetime.timedelta(hours=3), cache_dir=CACHE_DIR)
def busca_preco_atual(ticker):

    try:
        return preco_atual_yahoo(ticker)
    except:
        pass

    try:
        from src.crawler_advfn import CrawlerAdvfn
        crawlerAdvfn = CrawlerAdvfn()

        preco_atual = crawlerAdvfn.busca_preco_atual(ticker)

        if preco_atual is not None:
            return preco_atual
    except:
        pass

    return None