from unittest import TestCase
from src.tipo_ticker import TipoTicker
from tests.utils import get_random_opcoes_tickers
from src.tipo_ticker import tipo_ticker
from src.utils import ano_corrente


class TestTipoTicker(TestCase):

    def setup_method(self, method):
        tipo_ticker.clear_cache()

    def test_tipo_ticker(self):
        assert tipo_ticker('whgr11') is TipoTicker.FII
        assert tipo_ticker('MSFT34') is TipoTicker.BDR
        assert tipo_ticker('ISPU' + ano_corrente()) is TipoTicker.FUTURO
        assert tipo_ticker('CMIN3') is TipoTicker.ACAO
        assert tipo_ticker('GRLV11') is TipoTicker.FII
        assert tipo_ticker('VRTA11') is TipoTicker.FII
        assert tipo_ticker('vrta11') is TipoTicker.FII
        assert tipo_ticker('ITSA4') is TipoTicker.ACAO
        assert tipo_ticker('PETR4') is TipoTicker.ACAO
        assert tipo_ticker('BOVA11') is TipoTicker.ETF
        assert tipo_ticker('SPXI11') is TipoTicker.ETF
        assert tipo_ticker(get_random_opcoes_tickers()[0]) is TipoTicker.OPCAO
        assert tipo_ticker(get_random_opcoes_tickers()[1]) is TipoTicker.OPCAO
        assert tipo_ticker('IRDM11') is TipoTicker.FII
        assert tipo_ticker('invalid') is None
