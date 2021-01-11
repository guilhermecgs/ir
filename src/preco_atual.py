from src.crawler_yahoo import busca_preco_atual as preco_atual_yahoo
from cachier import cachier
import datetime

@cachier(stale_after=datetime.timedelta(days=1))
def busca_preco_atual(ticker):
    try:
        preco_atual = preco_atual_yahoo(ticker)
        return preco_atual
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