from unittest import TestCase
from src.tipo_ticker import TipoTicker
from tests.utils import get_random_opcoes_tickers
from src.tipo_ticker import tipo_ticker
from src.utils import ano_corrente


class TestTipoTicker(TestCase):

    def setup_method(self, method):
        tipo_ticker.clear_cache()

    def test_tipo_ticker(self):
        assert tipo_ticker('ELET6') is TipoTicker.ACAO_OU_ETF
        assert tipo_ticker('TRPL4') is TipoTicker.ACAO_OU_ETF
        assert tipo_ticker('VGIA11') is TipoTicker.FII
        assert tipo_ticker('ALUP11') is TipoTicker.ACAO_OU_ETF
        assert tipo_ticker('whgr11') is TipoTicker.FII
        assert tipo_ticker('RZAG11') is TipoTicker.FII
        assert tipo_ticker('AAZQ11') is TipoTicker.FII
        assert tipo_ticker('IRDM11') is TipoTicker.FII
        assert tipo_ticker('GRLV11') is TipoTicker.FII
        assert tipo_ticker('VRTA11') is TipoTicker.FII
        assert tipo_ticker('vrta11') is TipoTicker.FII
        assert tipo_ticker('ITSA4') is TipoTicker.ACAO_OU_ETF
        assert tipo_ticker('PETR4') is TipoTicker.ACAO_OU_ETF
        assert tipo_ticker('CMIN3') is TipoTicker.ACAO_OU_ETF
        assert tipo_ticker('BOVA11') is TipoTicker.ACAO_OU_ETF
        assert tipo_ticker('SPXI11') is TipoTicker.ACAO_OU_ETF
        assert tipo_ticker('MSFT34') is TipoTicker.BDR
        assert tipo_ticker('invalid') is None
        assert tipo_ticker('ISPU' + ano_corrente()) is TipoTicker.FUTURO
        assert tipo_ticker(get_random_opcoes_tickers()[0]) is TipoTicker.OPCAO
        assert tipo_ticker(get_random_opcoes_tickers()[1]) is TipoTicker.OPCAO

    def test_ibovespa_tickers_and_preservation(self):
        # Imports are usually at the top of the file,
        # but tipo_ticker and TipoTicker are already imported in the file scope of test_tipo_ticker.py
        # So, no need for local imports here if they are accessible.

        # Assertions for Ibovespa tickers
        assert tipo_ticker('PETR4') is TipoTicker.ACAO_OU_ETF
        assert tipo_ticker('VALE3') is TipoTicker.ACAO_OU_ETF
        assert tipo_ticker('ITUB4') is TipoTicker.ACAO_OU_ETF
        assert tipo_ticker('ABEV3') is TipoTicker.ACAO_OU_ETF

        # Assertions for preservation of other types
        assert tipo_ticker('XPIN11') is TipoTicker.FII  # Existing FII
        assert tipo_ticker('BBASP280W2') is TipoTicker.OPCAO  # Existing Option
        assert tipo_ticker('IVVB11') is TipoTicker.ACAO_OU_ETF  # Existing ETF
        
