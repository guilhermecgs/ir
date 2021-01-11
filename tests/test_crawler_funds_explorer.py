import unittest
from src.crawler_funds_explorer_bs4 import eh_tipo_fii, fii_dividend_yield, fii_p_vp, fii_razao_social, fii_nome, fii_cnpj


class TestCrawlerFundsExplorer(unittest.TestCase):

    def test_eh_tipo_fii(self):
        assert eh_tipo_fii('SDIL12')
        assert eh_tipo_fii('SDIL13')
        assert eh_tipo_fii('SDIL14')
        assert eh_tipo_fii('SDIL11')
        assert eh_tipo_fii('sdil11')
        assert eh_tipo_fii('MAXR11')
        assert eh_tipo_fii('maxr11')
        assert eh_tipo_fii('VRTA11')
        assert eh_tipo_fii('LVBI11')
        assert eh_tipo_fii('VILG12')
        assert not eh_tipo_fii('ITSA4')
        assert not eh_tipo_fii('BOVA11')
        assert not eh_tipo_fii('invalid')

    def test_fii_dividend_yield(self):
        assert isinstance(fii_dividend_yield('SDIL12'), float)
        assert isinstance(fii_dividend_yield('SDIL11'), float)
        assert isinstance(fii_dividend_yield('sdil11'), float)
        assert fii_dividend_yield('ITSA4') is None
        assert fii_dividend_yield('BOVA11') is None
        assert fii_dividend_yield('invalid') is None

    def test_fii_p_vp(self):
        assert isinstance(fii_p_vp('SDIL12'), float)
        assert isinstance(fii_p_vp('SDIL11'), float)
        assert isinstance(fii_p_vp('sdil11'), float)
        assert fii_p_vp('ITSA4') is None
        assert fii_p_vp('BOVA11') is None
        assert fii_p_vp('invalid') is None

    def test_fii_nome(self):
        assert fii_nome('XPML11') == 'XP MALLS FDO INV IMOB FII'
        assert fii_razao_social('XPML11') == 'XP MALLS FDO INV IMOB FII'
        assert fii_cnpj('XPML11') == '28.757.546/0001-00'
        
    