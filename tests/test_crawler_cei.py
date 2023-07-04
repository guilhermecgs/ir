# import os

# from src.crawler_cei import busca_trades
# import pandas as pd


# class TestCrawlerCei():

#     def test_busca_trades(self):
#         trades = busca_trades(os.environ['CPF'], os.environ['SENHA_CEI'])
#         assert type(trades) is pd.DataFrame
#         assert len(trades)