import unittest
import pytest
import pandas as pd
import datetime
from src.tipo_ticker import TipoTicker
from src.stuff import get_operations, check_split_operations, calcula_precos_medio_de_compra, \
    calcula_custodia, tipo_ticker, merge_operacoes, df_to_csv, vendas_no_mes, todas_as_colunas
from tests.utils import create_testing_dataframe, get_random_opcoes_tickers, OPERACOES_DE_TESTE



class TestStuff(unittest.TestCase):

    def test_deve_criar_dataframe_vazio_se_arquivo_vazio(self):
        df = get_operations('arquivo_invalido.txt')
        self.assertListEqual(list(df.columns), todas_as_colunas())

    def test_descobre_vendas_no_mes(self):
        data = [{'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 3, 11), 'preco': 100},
                {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 11), 'preco': 100},
                {'ticker': 'gcgs', 'qtd': -100, 'data': datetime.date(2019, 4, 12), 'preco': 200},
                {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 13), 'preco': 300},
                {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 14), 'preco': 400},
                {'ticker': 'gcgs', 'qtd': -200, 'data': datetime.date(2019, 4, 15), 'preco': 500},
                {'ticker': 'gcgs2', 'qtd': 200, 'data': datetime.date(2019, 4, 15), 'preco': 500},
                {'ticker': 'gcgs3', 'qtd': -200, 'data': datetime.date(2019, 4, 15), 'preco': 500},
                {'ticker': 'gcgs', 'qtd': -200, 'data': datetime.date(2019, 4, 15), 'preco': 500},
                {'ticker': 'gcgs', 'qtd': 2, 'data': datetime.date(2019, 4, 15), 'preco': 5},
                {'ticker': 'gcgs', 'qtd': -1, 'data': datetime.date(2019, 4, 15), 'preco': 1},
                {'ticker': 'gcgs', 'qtd': 3, 'data': datetime.date(2019, 4, 15), 'preco': 2},
                {'ticker': 'gcgs', 'qtd': 1, 'data': datetime.date(2019, 4, 16), 'preco': 2}]

        df = create_testing_dataframe(data)

        vendas_no_mes_abril = vendas_no_mes(df, 2019, 4)
        assert type(vendas_no_mes_abril) is list
        assert len(vendas_no_mes_abril) == 2

    def test_merge_operacoes_append_puro(self):
        data = [{'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 3, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'gcgs', 'qtd': -100, 'data': datetime.date(2019, 4, 12), 'preco': 200, 'aquisicao_via': 'HomeBroker'}]

        df = create_testing_dataframe(data)

        other_data = [{'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 10, 14), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                      {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 10, 15), 'preco': 100, 'aquisicao_via': 'HomeBroker'}]

        other_df = create_testing_dataframe(other_data)

        result = merge_operacoes(df, other_df)

        assert len(result) == (len(df) + len(other_df))

    def test_merge_operacoes_other_df_vazio(self):
        data = [{'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 3, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'gcgs', 'qtd': -100, 'data': datetime.date(2019, 4, 12), 'preco': 200, 'aquisicao_via': 'HomeBroker'}]

        df = create_testing_dataframe(data)

        other_df = create_testing_dataframe([])

        result = merge_operacoes(df, other_df)

        assert len(result) == len(df)

    def test_merge_operacoes_df_vazio(self):
        df = create_testing_dataframe([])

        other_data = [{'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 10, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                      {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 10, 12), 'preco': 100, 'aquisicao_via': 'HomeBroker'}]

        other_df = create_testing_dataframe(other_data)

        result = merge_operacoes(df, other_df)

        assert len(result) == len(other_df)

    def test_merge_operacoes_com_ipo(self):
        data = [{'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 3, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'}]

        other_data = [{'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 10, 13), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                      {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 10, 14), 'preco': 100, 'aquisicao_via': 'HomeBroker'}]
        other_data.extend(data)
        other_df = create_testing_dataframe(other_data)

        data.extend([{'ticker': 'gcgs', 'qtd': -100, 'data': datetime.date(2019, 4, 20), 'preco': 200, 'aquisicao_via': 'IPO'}])
        df = create_testing_dataframe(data)

        result = merge_operacoes(df, other_df)

        assert len(result) == (len(df) + 2)

    def test_merge_operacoes_com_ipo_em_uma_data_futura(self):
        data = [{'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 3, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'}]

        other_data = [{'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 10, 13), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                      {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 10, 14), 'preco': 100, 'aquisicao_via': 'HomeBroker'}]
        other_data.extend(data)
        other_df = create_testing_dataframe(other_data)

        data.extend([{'ticker': 'gcgs', 'qtd': -100, 'data': datetime.date(2099, 4, 20), 'preco': 200, 'aquisicao_via': 'IPO'}])
        df = create_testing_dataframe(data)

        result = merge_operacoes(df, other_df)

        assert len(result) == (len(df) + 2)

    def test_df_to_csv(self):
        df_original = get_operations(OPERACOES_DE_TESTE)
        assert len(df_original) > 0

        df_to_csv(df_original, 'df_to_csv_testing.txt')

        df_lido = get_operations('df_to_csv_testing.txt')
        assert df_lido.equals(df_original)

    def test_calcula_custodia(self):
        from src.dropbox_files import download_dropbox_file
        download_dropbox_file(OPERACOES_DE_TESTE)

        df = get_operations(OPERACOES_DE_TESTE)
        assert len(df) > 0
        df = df.tail(80)

        data = datetime.datetime.now().date()
        custodia = calcula_custodia(df, data)

        assert type(custodia) is pd.DataFrame
        assert 'preco_medio_compra' in custodia.columns
        assert 'ticker' in custodia.columns
        assert 'qtd' in custodia.columns
        assert 'preco_atual' in custodia.columns
        assert 'valorizacao' in custodia.columns
        assert 'ultimo_yield' in custodia.columns
        assert 'valor' in custodia.columns
        assert 'tipo' in custodia.columns
        assert 'data_primeira_compra' in custodia.columns

    def test_calcula_precos_medios_do_dropbox(self):
        from src.dropbox_files import download_dropbox_file
        download_dropbox_file(OPERACOES_DE_TESTE)

        df = get_operations(OPERACOES_DE_TESTE)
        assert len(df) > 0

        precos_medios_de_compra = calcula_precos_medio_de_compra(df)
        assert type(precos_medios_de_compra) is dict

    def test_calcula_precos_medios_quando_um_ciclo(self):
        data = [{'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 20), 'preco': 100},
                {'ticker': 'gcgs', 'qtd': 200, 'data': datetime.date(2019, 4, 13), 'preco': 200}]

        df = create_testing_dataframe(data)

        precos_medio_de_compra = calcula_precos_medio_de_compra(df)

        assert precos_medio_de_compra['gcgs']['valor'] == pytest.approx(166.66, 0.01)
        assert precos_medio_de_compra['gcgs']['data_primeira_compra'] == datetime.date(2019, 4, 13)

    def test_calcula_precos_medios_quando_varios_tickers_juntos(self):
        data = [{'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 20), 'preco': 100},
                {'ticker': 'gcgs2', 'qtd': 100, 'data': datetime.date(2019, 4, 20), 'preco': 100},
                {'ticker': 'gcgs2', 'qtd': 100, 'data': datetime.date(2019, 4, 20), 'preco': 100},
                {'ticker': 'gcgs2', 'qtd': 100, 'data': datetime.date(2019, 4, 20), 'preco': 100},
                {'ticker': 'gcgs', 'qtd': 200, 'data': datetime.date(2019, 4, 13), 'preco': 200}]

        df = create_testing_dataframe(data)

        precos_medio_de_compra = calcula_precos_medio_de_compra(df)

        assert precos_medio_de_compra['gcgs']['valor'] == pytest.approx(166.66, 0.01)
        assert precos_medio_de_compra['gcgs']['data_primeira_compra'] == datetime.date(2019, 4, 13)

    def test_calcula_precos_medios_quando_varios_ciclo(self):

        data = [{'ticker': 'gcgs', 'qtd': 1, 'data': datetime.date(2019, 4, 11), 'preco': 5},
                {'ticker': 'gcgs', 'qtd': -1, 'data': datetime.date(2019, 4, 12), 'preco': 6},
                {'ticker': 'gcgs', 'qtd': 2, 'data': datetime.date(2019, 4, 13), 'preco': 3},
                {'ticker': 'gcgs', 'qtd': -1, 'data': datetime.date(2019, 4, 14), 'preco': 2},
                {'ticker': 'gcgs', 'qtd': -1, 'data': datetime.date(2019, 4, 15), 'preco': 4},
                {'ticker': 'gcgs', 'qtd': 1, 'data': datetime.date(2019, 4, 15), 'preco': 2},
                {'ticker': 'gcgs', 'qtd': 1, 'data': datetime.date(2019, 4, 15), 'preco': 3},
                {'ticker': 'gcgs', 'qtd': 1, 'data': datetime.date(2019, 4, 15), 'preco': 4},
                {'ticker': 'gcgs', 'qtd': -2, 'data': datetime.date(2019, 4, 16), 'preco': 5}]

        df = create_testing_dataframe(data)
        precos_medio_de_compra = calcula_precos_medio_de_compra(df)
        assert precos_medio_de_compra['gcgs']['valor'] == pytest.approx(3.0, 0.001)

        data = [{'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 11), 'preco': 100},
                {'ticker': 'gcgs', 'qtd': -100, 'data': datetime.date(2019, 4, 12), 'preco': 200},
                {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 13), 'preco': 300},
                {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 14), 'preco': 400},
                {'ticker': 'gcgs', 'qtd': -200, 'data': datetime.date(2019, 4, 15), 'preco': 500},
                {'ticker': 'gcgs', 'qtd': 2, 'data': datetime.date(2019, 4, 16), 'preco': 5},
                {'ticker': 'gcgs', 'qtd': -1, 'data': datetime.date(2019, 4, 16), 'preco': 1},
                {'ticker': 'gcgs', 'qtd': 3, 'data': datetime.date(2019, 4, 17), 'preco': 2},
                {'ticker': 'gcgs', 'qtd': 1, 'data': datetime.date(2019, 4, 17), 'preco': 2}]

        df = create_testing_dataframe(data)
        precos_medio_de_compra = calcula_precos_medio_de_compra(df)

        assert precos_medio_de_compra['gcgs']['valor'] == pytest.approx(2.6, 0.001)
        assert precos_medio_de_compra['gcgs']['data_primeira_compra'] == datetime.date(2019, 4, 16)

    def test_calcula_precos_medios_quando_operacoes_no_mesmo_dia_estao_fora_de_ordem(self):
        # dentro de um mesmo dia, nao existe a informacao de horas.
        # logo, nao há garantia de que as operacoes ocorreram na ordem informada (dentro um mesmo dia)

        data = [{'ticker': 'gcgs', 'qtd': 100,  'data': datetime.date(2019, 4, 11), 'preco': 100},
                {'ticker': 'gcgs', 'qtd': -100, 'data': datetime.date(2019, 4, 12), 'preco': 200},
                {'ticker': 'gcgs', 'qtd': -200, 'data': datetime.date(2019, 4, 13), 'preco': 500},
                {'ticker': 'gcgs', 'qtd': 100,  'data': datetime.date(2019, 4, 13), 'preco': 300},
                {'ticker': 'gcgs', 'qtd': 100,  'data': datetime.date(2019, 4, 13), 'preco': 400},
                {'ticker': 'gcgs', 'qtd': -1,   'data': datetime.date(2019, 4, 15), 'preco': 1},
                {'ticker': 'gcgs', 'qtd': 2,    'data': datetime.date(2019, 4, 15), 'preco': 5},
                {'ticker': 'gcgs', 'qtd': 3,    'data': datetime.date(2019, 4, 15), 'preco': 2},
                {'ticker': 'gcgs', 'qtd': 1,    'data': datetime.date(2019, 4, 16), 'preco': 2}]

        df = create_testing_dataframe(data)
        precos_medio_de_compra = calcula_precos_medio_de_compra(df)

        assert precos_medio_de_compra['gcgs']['valor'] == pytest.approx(2.96, 0.001)
        assert precos_medio_de_compra['gcgs']['data_primeira_compra'] == datetime.date(2019, 4, 15)

    def test_tipo_ticker(self):
        assert tipo_ticker('GRLV11') is TipoTicker.FII
        assert tipo_ticker('VRTA11') is TipoTicker.FII
        assert tipo_ticker('ITSA4') is TipoTicker.ACAO
        assert tipo_ticker('PETR4') is TipoTicker.ACAO
        assert tipo_ticker('BOVA11') is TipoTicker.ETF
        assert tipo_ticker('SPXI11') is TipoTicker.ETF
        assert tipo_ticker('ISPU20') is TipoTicker.FUTURO
        assert tipo_ticker(get_random_opcoes_tickers()[0]) is TipoTicker.OPCAO
        assert tipo_ticker(get_random_opcoes_tickers()[1]) is TipoTicker.OPCAO
        assert tipo_ticker('IRDM11') is TipoTicker.FII
        assert tipo_ticker('invalid') is None

    def test_split_operations_by_defs(self):
        data = [{'ticker': 'id1:1|id2:3', 'qtd': 0,  'data': datetime.date(2019, 4, 11), 'preco': 0, 'taxas' : 4, 'aquisicao_via' : 'teste'}]

        df = create_testing_dataframe(data)

        split_data = check_split_operations(df)
        assert len(split_data) == 2
        assert split_data['ticker'][0] == 'id1'
        assert split_data['ticker'][1] == 'id2'
        assert split_data['taxas'][0] == 1
        assert split_data['taxas'][1] == 3


    def test_split_operations(self):
        data = [{'ticker': 'id1', 'qtd': 1,  'data': datetime.date(2019, 4, 11), 'preco': 100, 'taxas' : 0, 'aquisicao_via' : 'teste'},
                {'ticker': 'id2', 'qtd': 3,  'data': datetime.date(2019, 4, 11), 'preco': 100, 'taxas' : 0, 'aquisicao_via' : 'teste'},
                ]
        notas = [{'ticker': '@SPLIT', 'qtd': 0,  'data': datetime.date(2019, 4, 11), 'preco': 0, 'taxas' : 4.00, 'aquisicao_via' : 'teste'},                
                ]

        df = create_testing_dataframe(data)
        dfNotas = create_testing_dataframe(notas)

        split_data = check_split_operations(dfNotas, df)
        print(split_data)
        assert len(split_data) == 2
        assert split_data['ticker'][0] == 'id1'
        assert split_data['ticker'][1] == 'id2'
        assert split_data['taxas'][0] == 1
        assert split_data['taxas'][1] == 3

    def test_split_operations_com_venda(self):
        data = [{'ticker': 'id2', 'qtd': 3,  'data': datetime.date(2019, 3, 11), 'preco': 50, 'taxas' : 0, 'aquisicao_via' : 'teste'},
                {'ticker': 'id1', 'qtd': 1,  'data': datetime.date(2019, 4, 11), 'preco': 100, 'taxas' : 0, 'aquisicao_via' : 'teste'},
                {'ticker': 'id2', 'qtd': -3,  'data': datetime.date(2019, 4, 11), 'preco': 100, 'taxas' : 0, 'aquisicao_via' : 'teste'},
                ]
        notas = [{'ticker': '@SPLIT', 'qtd': 0,  'data': datetime.date(2019, 4, 11), 'preco': 0, 'taxas' : 4.00, 'aquisicao_via' : 'teste'},                
                ]

        df = create_testing_dataframe(data)
        dfNotas = create_testing_dataframe(notas)

        split_data = check_split_operations(dfNotas, df)
        print(split_data)
        assert len(split_data) == 2
        assert split_data['ticker'][0] == 'id1'
        assert split_data['ticker'][1] == 'id2'
        assert split_data['taxas'][0] == 1
        assert split_data['taxas'][1] == 3
        assert split_data['valor'][0] == 0
        assert split_data['valor'][1] == 0
