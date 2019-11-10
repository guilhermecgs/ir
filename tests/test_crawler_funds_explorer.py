import unittest
from src.crawler_funds_explorer_bs4 import e_tipo_fii

class TestCrawlerFundsExplorer(unittest.TestCase):

    def test_get_ticker_price_bs4(self):
        assert e_tipo_fii('MAXR11')
        assert e_tipo_fii('maxr11')
        assert e_tipo_fii('VRTA11')
        assert e_tipo_fii('LVBI11')

        assert not e_tipo_fii('ITSA4')
        assert not e_tipo_fii('BOVA11')
        assert not e_tipo_fii('invalid')

