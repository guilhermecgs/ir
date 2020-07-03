from src.crawler_yahoo_bs4 import busca_preco_atual as preco_atual_yahoo

__cache__ = {}


def busca_preco_atual(ticker):
    if ticker in __cache__:
        return __cache__[ticker]
    else:
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