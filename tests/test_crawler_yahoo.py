import unittest
from src.crawler_yahoo import parse

class TestCrawlerYahoo(unittest.TestCase):

    def test_get_ticker_price(self):
        itsa4 = parse('ITSA4.SA')
        print(itsa4)

        vrta11 = parse('VRTA11.SA')
        print(vrta11)

        bova11 = parse('BOVA11.SA')
        print(bova11)

        assert type(itsa4) is dict
        assert type(vrta11) is dict
        assert type(bova11) is dict

        assert 'error' not in itsa4
        assert 'error' not in vrta11
        assert 'error' not in bova11
