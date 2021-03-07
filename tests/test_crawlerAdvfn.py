from src.crawler_advfn import advfn_tipo_ticker, advfn_preco_atual
from src.tipo_ticker import TipoTicker


class TestCrawlerAdvfn():

    def test_busca_preco_atual(self):
        assert advfn_preco_atual('INVALID_ticker') is None
        assert type(advfn_preco_atual('SDIL11')) is float
        assert type(advfn_preco_atual('ITSA4')) is float
        assert type(advfn_preco_atual('BOVA11')) is float
        assert type(advfn_preco_atual('BABA34')) is float
        assert advfn_preco_atual('SDIL11') == advfn_preco_atual('sdil11')

    def test_busca_tipo_ticker(self):
        assert advfn_tipo_ticker('ISPU20') == TipoTicker.FUTURO
        assert advfn_tipo_ticker('PETRA253') == TipoTicker.OPCAO
        assert advfn_tipo_ticker('INVALID') is None
        assert advfn_tipo_ticker('SDIL11') == TipoTicker.FII
        assert advfn_tipo_ticker('BOVA11') == TipoTicker.ETF
        assert advfn_tipo_ticker('ITSA4') == TipoTicker.ACAO
        assert advfn_tipo_ticker('ITSA4') == advfn_tipo_ticker('itsa4')
        assert advfn_tipo_ticker('AAPL34') == TipoTicker.BDR
        assert advfn_tipo_ticker('BABA34') == TipoTicker.BDR
