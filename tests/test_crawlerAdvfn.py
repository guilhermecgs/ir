import unittest.mock as mock
from unittest import TestCase

from src import crawler_advfn
from src.crawler_advfn import CrawlerAdvfn
from src.tipo_ticker import TipoTicker


class TestCrawlerAdvfn(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.advfn = CrawlerAdvfn()

    def __reset_cache(self):
        crawler_advfn.cache = {}

    def test_deve_buscar_apenas_uma_vez_na_advfn(self):
        self.__reset_cache()

        return_value = {'tipo_ticker': TipoTicker.ACAO, 'preco_atual': 666}
        with mock.patch.object(self.advfn, '_CrawlerAdvfn__recupera_informacoes', return_value=return_value) as method:
            self.advfn.busca_preco_atual('ACAO11')
            self.advfn.busca_preco_atual('ACAO11')
            self.advfn.busca_tipo_ticker('ACAO11')
            self.advfn.busca_preco_atual('ACAO12')
            self.advfn.busca_preco_atual('ACAO12')
            self.advfn.busca_tipo_ticker('ACAO12')
            assert method.call_count == 2

    def test_busca_preco_atual(self):
        assert self.advfn.busca_preco_atual('INVALID') is None
        assert type(self.advfn.busca_preco_atual('SDIL11')) is float
        assert type(self.advfn.busca_preco_atual('MAXR11')) is float
        assert type(self.advfn.busca_preco_atual('ITSA4')) is float
        assert type(self.advfn.busca_preco_atual('VRTA11')) is float
        assert type(self.advfn.busca_preco_atual('BOVA11')) is float
        assert type(self.advfn.busca_preco_atual('ABEVH222')) is float
        assert type(self.advfn.busca_preco_atual('ABEVT40')) is float
        assert type(self.advfn.busca_preco_atual('ABEVT45')) is float
        assert type(self.advfn.busca_preco_atual('AZULG525')) is float
        assert type(self.advfn.busca_preco_atual('PETRG229')) is float
        assert type(self.advfn.busca_preco_atual('IRBRH115')) is float
        assert type(self.advfn.busca_preco_atual('ABEVS41')) is float
        assert type(self.advfn.busca_preco_atual('MRFGH18')) is float
        assert type(self.advfn.busca_preco_atual('CMIGG14')) is float
        assert type(self.advfn.busca_preco_atual('COGNG7')) is float
        assert type(self.advfn.busca_preco_atual('ISPU20')) is float
        assert type(self.advfn.busca_preco_atual('WSPU20')) is float
        assert self.advfn.busca_preco_atual('SDIL11') == self.advfn.busca_preco_atual('sdil11')

    def test_busca_tipo_ticker(self):
        assert self.advfn.busca_tipo_ticker('INVALID') is None
        assert self.advfn.busca_tipo_ticker('SDIL11') == TipoTicker.FII
        assert self.advfn.busca_tipo_ticker('MAXR11') == TipoTicker.FII
        assert self.advfn.busca_tipo_ticker('VRTA11') == TipoTicker.FII
        assert self.advfn.busca_tipo_ticker('VILG11') == TipoTicker.FII
        assert self.advfn.busca_tipo_ticker('BOVA11') == TipoTicker.ETF
        assert self.advfn.busca_tipo_ticker('DIVO11') == TipoTicker.ETF
        assert self.advfn.busca_tipo_ticker('SPXI11') == TipoTicker.ETF
        assert self.advfn.busca_tipo_ticker('ISPU20') == TipoTicker.FUTURO
        assert self.advfn.busca_tipo_ticker('WSPU20') == TipoTicker.FUTURO
        assert self.advfn.busca_tipo_ticker('ITSA4') == TipoTicker.ACAO
        assert self.advfn.busca_tipo_ticker('ABEVH222') == TipoTicker.OPCAO
        assert self.advfn.busca_tipo_ticker('ABEVT40') == TipoTicker.OPCAO
        assert self.advfn.busca_tipo_ticker('ABEVT45') == TipoTicker.OPCAO
        assert self.advfn.busca_tipo_ticker('AZULG525') == TipoTicker.OPCAO
        assert self.advfn.busca_tipo_ticker('PETRG229') == TipoTicker.OPCAO
        assert self.advfn.busca_tipo_ticker('IRBRH115') == TipoTicker.OPCAO
        assert self.advfn.busca_tipo_ticker('ABEVS41') == TipoTicker.OPCAO
        assert self.advfn.busca_tipo_ticker('MRFGH18') == TipoTicker.OPCAO
        assert self.advfn.busca_tipo_ticker('CMIGG14') == TipoTicker.OPCAO
        assert self.advfn.busca_tipo_ticker('COGNG7') == TipoTicker.OPCAO
        assert self.advfn.busca_tipo_ticker('ITSA4') == self.advfn.busca_tipo_ticker('itsa4')
