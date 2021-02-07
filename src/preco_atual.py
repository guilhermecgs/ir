from src.crawler_yahoo import busca_preco_atual as preco_atual_yahoo
from src.dados import ticker_equivalente, ticker_data
from cachier import cachier
import datetime

def busca_preco_atual(ticker):
    ticker = ticker_equivalente(ticker)
    cotacao = ticker_data(ticker, 'cotacao')
    if cotacao:
        return cotacao
    return __busca_preco_atual(ticker)
        
@cachier(stale_after=datetime.timedelta(days=1))
def __busca_preco_atual(ticker):
    try:
        preco_atual = preco_atual_yahoo(ticker)
        return preco_atual
    except:
        pass

    try:
        from src.crawler_advfn import advfn_preco_atual

        preco_atual = advfn_preco_atual(ticker)

        if preco_atual is not None:
            return preco_atual
    except:
        pass

    return float('nan')
    