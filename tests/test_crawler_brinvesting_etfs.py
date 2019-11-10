import unittest
from src.crawler_brinvesting_etfs import e_tipo_etf


class TestCrawlerBrInvest(unittest.TestCase):

    def test_crawler(self):
        assert e_tipo_etf('BOVA11')
        assert e_tipo_etf('bova11')
        assert e_tipo_etf('DIVO11')

        assert not e_tipo_etf('ITSA4')
        assert not e_tipo_etf('VRTA11')
        assert not e_tipo_etf('invalid')

