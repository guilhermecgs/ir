# import unittest
# import pytest
# import pandas as pd
# import datetime
# from src.domain.tipo_ticker import TipoTicker
# from src.stuff import get_operations_dataframe, calcula_precos_medio_de_compra, \
#     calcula_custodia, vendas_no_mes, calcula_valor, tipo_ticker
#
#
# class TestStuff(unittest.TestCase):
#
#     def test_descobre_vendas_no_mes(self):
#         data = [{'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 3, 11), 'preco': 100},
#                 {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 11), 'preco': 100},
#                 {'ticker': 'gcgs', 'qtd': -100, 'data': datetime.date(2019, 4, 12), 'preco': 200},
#                 {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 13), 'preco': 300},
#                 {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 14), 'preco': 400},
#                 {'ticker': 'gcgs', 'qtd': -200, 'data': datetime.date(2019, 4, 15), 'preco': 500},
#                 {'ticker': 'gcgs2', 'qtd': -200, 'data': datetime.date(2019, 4, 15), 'preco': 500},
#                 {'ticker': 'gcgs', 'qtd': 2, 'data': datetime.date(2019, 4, 15), 'preco': 5},
#                 {'ticker': 'gcgs', 'qtd': -1, 'data': datetime.date(2019, 4, 15), 'preco': 1},
#                 {'ticker': 'gcgs', 'qtd': 3, 'data': datetime.date(2019, 4, 15), 'preco': 2},
#                 {'ticker': 'gcgs', 'qtd': 1, 'data': datetime.date(2019, 4, 16), 'preco': 2}]
#
#         df = pd.DataFrame(data)
#         df['valor'] = df.apply(lambda row: calcula_valor(row.qtd, row.preco), axis=1)
#
#         vendas_no_mes_abril = vendas_no_mes(df, 2019, 4)
#         assert type(vendas_no_mes_abril) is list
#         assert len(vendas_no_mes_abril) == 2
#
#     def test_calcula_custodia(self):
#         from src.dropbox_files import download_dropbox_file
#         download_dropbox_file()
#
#         df = get_operations_dataframe()
#
#         data = datetime.datetime.now().date()
#         custodia = calcula_custodia(df, data)
#
#         assert type(custodia) is pd.DataFrame
#         assert 'preco_medio_compra' in custodia.columns
#         assert 'ticker' in custodia.columns
#         assert 'qtd' in custodia.columns
#         assert 'preco_atual' in custodia.columns
#         assert 'valorizacao' in custodia.columns
#         assert 'valor' in custodia.columns
#         assert 'tipo' in custodia.columns
#         assert 'data_primeira_compra' in custodia.columns
#
#     def test_calcula_precos_medios_do_dropbox(self):
#         from src.dropbox_files import download_dropbox_file
#         download_dropbox_file()
#
#         df = get_operations_dataframe()
#
#         precos_medios_de_compra = calcula_precos_medio_de_compra(df)
#         assert type(precos_medios_de_compra) is dict
#
#     def test_calcula_precos_medios_quando_um_ciclo(self):
#         data = [{'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 20), 'preco': 100},
#                 {'ticker': 'gcgs', 'qtd': 200, 'data': datetime.date(2019, 4, 13), 'preco': 200}]
#
#         df = pd.DataFrame(data)
#         df['valor'] = df.apply(lambda row: calcula_valor(row.qtd, row.preco), axis=1)
#
#         precos_medio_de_compra = calcula_precos_medio_de_compra(df)
#
#         assert precos_medio_de_compra['gcgs']['valor'] == pytest.approx(166.66, 0.01)
#         assert precos_medio_de_compra['gcgs']['data_primeira_compra'] == datetime.date(2019, 4, 13)
#
#     def test_calcula_precos_medios_quando_varios_ciclo(self):
#         data = [{'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 11), 'preco': 100},
#                 {'ticker': 'gcgs', 'qtd': -100, 'data': datetime.date(2019, 4, 12), 'preco': 200},
#                 {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 13), 'preco': 300},
#                 {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 14), 'preco': 400},
#                 {'ticker': 'gcgs', 'qtd': -200, 'data': datetime.date(2019, 4, 15), 'preco': 500},
#                 {'ticker': 'gcgs', 'qtd': 2, 'data': datetime.date(2019, 4, 15), 'preco': 5},
#                 {'ticker': 'gcgs', 'qtd': -1, 'data': datetime.date(2019, 4, 15), 'preco': 1},
#                 {'ticker': 'gcgs', 'qtd': 3, 'data': datetime.date(2019, 4, 15), 'preco': 2},
#                 {'ticker': 'gcgs', 'qtd': 1, 'data': datetime.date(2019, 4, 16), 'preco': 2}]
#
#         df = pd.DataFrame(data)
#         df['valor'] = df.apply(lambda row: calcula_valor(row.qtd, row.preco), axis=1)
#
#         precos_medio_de_compra = calcula_precos_medio_de_compra(df)
#
#         assert precos_medio_de_compra['gcgs']['valor'] == pytest.approx(3, 0.001)
#         assert precos_medio_de_compra['gcgs']['data_primeira_compra'] == datetime.date(2019, 4, 15)
#
#     def test_tipo_ticker(self):
#         assert tipo_ticker('GRLV11') is TipoTicker.FII
#         assert tipo_ticker('SDIL11') is TipoTicker.FII
#         assert tipo_ticker('MAXR11') is TipoTicker.FII
#         assert tipo_ticker('maxr11') is TipoTicker.FII
#         assert tipo_ticker('VRTA11') is TipoTicker.FII
#         assert tipo_ticker('ITSA4') is TipoTicker.ACAO
#         assert tipo_ticker('itsa4') is TipoTicker.ACAO
#         assert tipo_ticker('BOVA11') is TipoTicker.ETF
#         assert tipo_ticker('bova11') is TipoTicker.ETF
#         assert tipo_ticker('MAXR11invalid') is None
#         assert tipo_ticker('invalid') is None