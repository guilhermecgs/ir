import unittest

from src.crawler_cei import busca_trades
import pandas as pd


class TestCrawlerCei(unittest.TestCase):

    def test_busca_trades(self):
        directory = '../public/'
        import os
        if not os.path.exists(directory):
            os.makedirs(directory)

        trades = busca_trades(os.environ['CPF'], os.environ['SENHA_CEI'])
        assert type(trades) is pd.DataFrame
        assert len(trades)