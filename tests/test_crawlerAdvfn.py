from src.crawler_advfn import advfn_tipo_ticker, advfn_preco_atual, busca_parametros
from src.tipo_ticker import TipoTicker
from src.utils import ano_corrente

class TestCrawlerAdvfn():

    def test_busca_preco_atual(self):
        busca_parametros.clear_cache()
        assert type(advfn_preco_atual('SDIL11')) is float
        assert advfn_preco_atual('INVALID_ticker') is None
        assert type(advfn_preco_atual('ITSA4')) is float
        assert type(advfn_preco_atual('BOVA11')) is float
        assert type(advfn_preco_atual('BABA34')) is float
        assert type(advfn_preco_atual('MELI34')) is float

    def test_busca_tipo_ticker(self):
        busca_parametros.clear_cache()
        assert advfn_tipo_ticker('SDIL11') == TipoTicker.FII
        assert advfn_tipo_ticker('BOVA11') == TipoTicker.ETF
        assert advfn_tipo_ticker('MAXR11') == TipoTicker.FII
        assert advfn_tipo_ticker('ISPU' + ano_corrente()) == TipoTicker.FUTURO
        assert advfn_tipo_ticker('INVALID') is None
        assert advfn_tipo_ticker('ITSA4') == TipoTicker.ACAO
        assert advfn_tipo_ticker('ITSA4') == advfn_tipo_ticker('itsa4')
        assert advfn_tipo_ticker('AAPL34') == TipoTicker.BDR
        assert advfn_tipo_ticker('BABA34') == TipoTicker.BDR
        assert advfn_tipo_ticker('MELI34') == TipoTicker.BDR
