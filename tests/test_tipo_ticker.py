from unittest import TestCase
from src.tipo_ticker import TipoTicker
from tests.utils import get_random_opcoes_tickers
from src.tipo_ticker import tipo_ticker


class TestTipoTicker(TestCase):

    def test_tipo_ticker(self):
        assert tipo_ticker('GRLV11') is TipoTicker.FII
        assert tipo_ticker('VRTA11') is TipoTicker.FII
        assert tipo_ticker('vrta11') is TipoTicker.FII
        assert tipo_ticker('ITSA4') is TipoTicker.ACAO
        assert tipo_ticker('PETR4') is TipoTicker.ACAO
        assert tipo_ticker('BOVA11') is TipoTicker.ETF
        assert tipo_ticker('SPXI11') is TipoTicker.ETF
        assert tipo_ticker('ISPU20') is TipoTicker.FUTURO
        assert tipo_ticker(get_random_opcoes_tickers()[0]) is TipoTicker.OPCAO
        assert tipo_ticker(get_random_opcoes_tickers()[1]) is TipoTicker.OPCAO
        assert tipo_ticker('IRDM11') is TipoTicker.FII
        assert tipo_ticker('invalid') is None
