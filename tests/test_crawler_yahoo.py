import unittest
from src.crawler_yahoo_bs4 import busca_preco_atual


class TestCrawlerYahoo(unittest.TestCase):

    def test_get_ticker_price_bs4(self):

        with self.assertRaises(Exception):
            busca_preco_atual('invalid')


        maxr11 = busca_preco_atual('MAXR11')
        print(maxr11)

        itsa4 = busca_preco_atual('ITSA4')
        print(itsa4)

        vrta11 = busca_preco_atual('VRTA11')
        print(vrta11)

        bova11 = busca_preco_atual('BOVA11')
        print(bova11)

        assert type(itsa4) is float
        assert type(vrta11) is float
        assert type(bova11) is float
