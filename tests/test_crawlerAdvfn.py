import unittest.mock as mock
from unittest import TestCase

from src.crawler_advfn import advfn_preco_atual, advfn_tipo_ticker, advfn_p_vp
from src.tipo_ticker import TipoTicker
from tests.utils import get_random_opcoes_tickers


class TestCrawlerAdvfn(TestCase):

    def test_busca_preco_atual(self):
#	PETRA253 venceu e não vem com valor....
#        assert type(advfn_preco_atual('PETRA253')) is float
        assert advfn_preco_atual('INVALID_ticker') is None
        assert type(advfn_preco_atual('SDIL11')) is float
        assert type(advfn_preco_atual('ITSA4')) is float
        assert type(advfn_preco_atual('BOVA11')) is float
        assert type(advfn_preco_atual('GMCO34')) is float
        assert advfn_preco_atual('SDIL11') == advfn_preco_atual('sdil11')

    def test_busca_tipo_ticker(self):
        assert advfn_tipo_ticker('ISPU20') == TipoTicker.FUTURO
        assert advfn_tipo_ticker('PETRA253') == TipoTicker.OPCAO
        assert advfn_tipo_ticker('INVALID') is None
        assert advfn_tipo_ticker('SDIL11') == TipoTicker.FII
        assert advfn_tipo_ticker('BOVA11') == TipoTicker.ETF
        assert advfn_tipo_ticker('GMCO34') == TipoTicker.BDR
        assert advfn_tipo_ticker('ITSA4') == TipoTicker.ACAO
        assert advfn_tipo_ticker('ITSA4') == advfn_tipo_ticker('itsa4')

    def test_busca_p_vp(self):
        assert type(advfn_p_vp('ITSA4')) is float
        assert advfn_p_vp('ITSA4') == advfn_p_vp('itsa4')
        # Somente acoes tem p_vp 
        assert advfn_p_vp('INVALID_ticker') is None
        assert advfn_p_vp('SDIL11') is None
        assert advfn_p_vp('BOVA11') is None
        assert advfn_p_vp('GMCO34') is None
