import unittest

from src.crawler_cei import CrawlerCei
import pandas as pd


class TestCrawlerCei(unittest.TestCase):

    def test_busca_trades(self):
        directory = '../public/'
        import os
        if not os.path.exists(directory):
            os.makedirs(directory)

        crawler_cei = CrawlerCei(headless=True, directory=directory, debug=True)
        trades = crawler_cei.busca_trades()
        assert type(trades) is pd.DataFrame
        assert len(trades)