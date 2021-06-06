from src.crawler_fiis import eh_tipo_fii, fii_dividend_yield


class TestCrawlerFiis():

    def test_eh_tipo_fii(self):
        assert eh_tipo_fii('HGLG11')
        assert eh_tipo_fii('HGLG12')
        assert eh_tipo_fii('SDIL12')
        assert eh_tipo_fii('SDIL11')
        assert eh_tipo_fii('sdil11')
        assert eh_tipo_fii('MAXR11')
        assert eh_tipo_fii('bari11')
        assert eh_tipo_fii('maxr11')
        assert eh_tipo_fii('VRTA11')
        assert eh_tipo_fii('LVBI11')
        assert eh_tipo_fii('VILG12')
        assert eh_tipo_fii('vilg11')
        assert not eh_tipo_fii('ITSA4')
        assert not eh_tipo_fii('BOVA11')
        assert not eh_tipo_fii('invalid')

    def test_fii_dividend_yield(self):
        assert isinstance(fii_dividend_yield('ALZR11'), float)
        assert isinstance(fii_dividend_yield('SDIL12'), float)
        assert isinstance(fii_dividend_yield('SDIL11'), float)
        assert isinstance(fii_dividend_yield('sdil11'), float)
        assert fii_dividend_yield('ITSA4') is None
        assert fii_dividend_yield('BOVA11') is None
        assert fii_dividend_yield('invalid') is None
