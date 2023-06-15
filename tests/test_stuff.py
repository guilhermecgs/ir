import pytest
import pandas as pd
import random
import string
from datetime import date


from src.stuff import get_operations, calcula_precos_medios_de_compra, calcula_preco_medio_de_compra, \
    calcula_custodia, merge_operacoes, df_to_csv, vendas_no_mes, todas_as_colunas, check_tipo_ticker

from tests.utils import create_testing_dataframe


def random_ticker():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))


class TestStuff():

    def setup_method(self, method):
        calcula_precos_medios_de_compra.clear_cache()

    def test_deve_criar_dataframe_vazio_se_arquivo_vazio(self):
        df = get_operations('arquivo_invalido.txt')
        assert list(df.columns) == todas_as_colunas()

    def test_descobre_vendas_no_mes(self):
        ticker = random_ticker()

        data = [{'ticker': ticker, 'qtd': 100, 'data': date(2019, 3, 11), 'preco': 100},
                {'ticker': ticker, 'qtd': 100, 'data': date(2019, 4, 11), 'preco': 100},
                {'ticker': ticker, 'qtd': -100, 'data': date(2019, 4, 12), 'preco': 200},
                {'ticker': ticker, 'qtd': 100, 'data': date(2019, 4, 13), 'preco': 300},
                {'ticker': ticker, 'qtd': 100, 'data': date(2019, 4, 14), 'preco': 400},
                {'ticker': ticker, 'qtd': -200, 'data': date(2019, 4, 15), 'preco': 500},
                {'ticker': random_ticker(), 'qtd': 200, 'data': date(2019, 4, 15), 'preco': 500},
                {'ticker': random_ticker(), 'qtd': -200, 'data': date(2019, 4, 15), 'preco': 500},
                {'ticker': ticker, 'qtd': -200, 'data': date(2019, 4, 15), 'preco': 500},
                {'ticker': ticker, 'qtd': 2, 'data': date(2019, 4, 15), 'preco': 5},
                {'ticker': ticker, 'qtd': -1, 'data': date(2019, 4, 15), 'preco': 1},
                {'ticker': ticker, 'qtd': 3, 'data': date(2019, 4, 15), 'preco': 2},
                {'ticker': ticker, 'qtd': 1, 'data': date(2019, 4, 16), 'preco': 2}]

        df = create_testing_dataframe(data)

        vendas_no_mes_abril = vendas_no_mes(df, 2019, 4)
        assert type(vendas_no_mes_abril) is list
        assert len(vendas_no_mes_abril) == 2

    def test_descobre_vendas_no_mes_deve_considerar_varios_ciclos_dentro_de_um_mesmo_mes(self):
        ticker = random_ticker()

        data = [{'ticker': ticker, 'qtd': 100, 'data': date(2019, 3, 11), 'preco': 150},
                {'ticker': ticker, 'qtd': 100, 'data': date(2019, 4, 11), 'preco': 100},
                {'ticker': ticker, 'qtd': -200, 'data': date(2019, 4, 12), 'preco': 200},
                {'ticker': ticker, 'qtd': 200, 'data': date(2019, 4, 13), 'preco': 300},
                {'ticker': ticker, 'qtd': 200, 'data': date(2019, 4, 14), 'preco': 400},
                {'ticker': ticker, 'qtd': -300, 'data': date(2019, 4, 15), 'preco': 500}]

        df = create_testing_dataframe(data)

        vendas_no_mes_abril = vendas_no_mes(df, 2019, 4)
        assert type(vendas_no_mes_abril) is list
        assert len(vendas_no_mes_abril) == 2
        assert vendas_no_mes_abril[0] == {'ticker': ticker, 'qtd_vendida': 200, 'preco_medio_venda': 200.0,
                                          'preco_medio_compra': 125.0, 'resultado_apurado': 15000.0}
        assert vendas_no_mes_abril[1] == {'ticker': ticker, 'qtd_vendida': 300, 'preco_medio_venda': 500.0,
                                          'preco_medio_compra': 350.0, 'resultado_apurado': 45000.0}

    def test_descobre_vendas_no_mes_quando_mais_de_um_ciclo_no_mesmo_mes(self):
        ticker = random_ticker()

        data = [{'ticker': ticker, 'qtd': 100, 'data': date(2019, 3, 11), 'preco': 100},
                {'ticker': ticker, 'qtd': 100, 'data': date(2019, 3, 12), 'preco': 100},
                {'ticker': ticker, 'qtd': -200, 'data': date(2019, 3, 13), 'preco': 200},
                {'ticker': ticker, 'qtd': 500, 'data': date(2019, 3, 14), 'preco': 300},
                {'ticker': ticker, 'qtd': -500, 'data': date(2019, 3, 15), 'preco': 400}]

        df = create_testing_dataframe(data)

        vendas_no_mes_abril = vendas_no_mes(df, 2019, 3)
        assert type(vendas_no_mes_abril) is list
        assert len(vendas_no_mes_abril) == 2

    def test_descobre_vendas_no_mes_quando_mais_de_uma_compra_venda_e_dentro_do_mesmo_ciclo(self):
        ticker = random_ticker()

        data = [{'ticker': ticker, 'qtd': 100, 'data': date(2019, 3, 11), 'preco': 100},
                {'ticker': ticker, 'qtd': 100, 'data': date(2019, 3, 12), 'preco': 100},
                {'ticker': ticker, 'qtd': -50, 'data': date(2019, 3, 13), 'preco': 200},
                {'ticker': ticker, 'qtd': 500, 'data': date(2019, 3, 14), 'preco': 300},
                {'ticker': ticker, 'qtd': -400, 'data': date(2019, 3, 15), 'preco': 400}]

        df = create_testing_dataframe(data)

        vendas_no_mes_abril = vendas_no_mes(df, 2019, 3)
        assert type(vendas_no_mes_abril) is list
        assert len(vendas_no_mes_abril) == 2
        assert vendas_no_mes_abril[0]['preco_medio_compra'] == pytest.approx(100.0, 0.001)
        assert vendas_no_mes_abril[0]['qtd_vendida'] == 50
        assert vendas_no_mes_abril[1]['preco_medio_compra'] == pytest.approx(253.84, 0.1)
        assert vendas_no_mes_abril[1]['qtd_vendida'] == 400

    def test_descobre_vendas_no_mes_quando_mais_de_uma_compra_venda_e_dentro_do_mesmo_ciclo_mas_com_mesmo_preco_de_compra(self):
        ticker = random_ticker()

        data = [{'ticker': ticker, 'qtd': 100, 'data': date(2019, 3, 11), 'preco': 100},
                {'ticker': ticker, 'qtd': 100, 'data': date(2019, 3, 12), 'preco': 100},
                {'ticker': ticker, 'qtd': -50, 'data': date(2019, 3, 13), 'preco': 200},
                {'ticker': ticker, 'qtd': 500, 'data': date(2019, 3, 14), 'preco': 100},
                {'ticker': ticker, 'qtd': -400, 'data': date(2019, 3, 15), 'preco': 400}]

        df = create_testing_dataframe(data)

        vendas_no_mes_abril = vendas_no_mes(df, 2019, 3)
        assert type(vendas_no_mes_abril) is list
        assert len(vendas_no_mes_abril) == 1
        assert vendas_no_mes_abril[0]['preco_medio_compra'] == pytest.approx(100.0, 0.001)
        assert vendas_no_mes_abril[0]['qtd_vendida'] == 450

    def test_merge_operacoes_append_puro(self):
        ticker = random_ticker()

        data = [{'ticker': ticker, 'qtd': 100, 'data': date(2019, 3, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                {'ticker': ticker, 'qtd': 100, 'data': date(2019, 4, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                {'ticker': ticker, 'qtd': -100, 'data': date(2019, 4, 12), 'preco': 200, 'aquisicao_via': 'HomeBroker'}]

        df = create_testing_dataframe(data)

        ticker2 = random_ticker()
        other_data = [{'ticker': ticker2, 'qtd': 100, 'data': date(2019, 10, 14), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                      {'ticker': ticker2, 'qtd': 100, 'data': date(2019, 10, 15), 'preco': 100, 'aquisicao_via': 'HomeBroker'}]

        other_df = create_testing_dataframe(other_data)

        result = merge_operacoes(df, other_df)

        assert len(result) == (len(df) + len(other_df))

    def test_merge_operacoes_other_df_eh_none(self):
        ticker = random_ticker()

        data = [{'ticker': ticker, 'qtd': 100, 'data': date(2019, 3, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                {'ticker': ticker, 'qtd': 100, 'data': date(2019, 4, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                {'ticker': ticker, 'qtd': -100, 'data': date(2019, 4, 12), 'preco': 200, 'aquisicao_via': 'HomeBroker'}]

        df = create_testing_dataframe(data)

        with pytest.raises(AssertionError):
            merge_operacoes(df, None)

    def test_merge_operacoes_df_eh_none(self):
        ticker = random_ticker()

        other_data = [{'ticker': ticker, 'qtd': 100, 'data': date(2019, 10, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                      {'ticker': ticker, 'qtd': 100, 'data': date(2019, 10, 12), 'preco': 100, 'aquisicao_via': 'HomeBroker'}]

        other_df = create_testing_dataframe(other_data)

        with pytest.raises(AssertionError):
            merge_operacoes(None, other_df)

    def test_merge_operacoes_other_df_vazio(self):
        ticker = random_ticker()

        data = [{'ticker': ticker, 'qtd': 100, 'data': date(2019, 3, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                {'ticker': ticker, 'qtd': 100, 'data': date(2019, 4, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                {'ticker': ticker, 'qtd': -100, 'data': date(2019, 4, 12), 'preco': 200, 'aquisicao_via': 'HomeBroker'}]

        df = create_testing_dataframe(data)

        other_df = create_testing_dataframe([])

        result = merge_operacoes(df, other_df)

        assert len(result) == len(df)

    def test_merge_operacoes_df_vazio(self):
        ticker = random_ticker()

        df = create_testing_dataframe([])

        other_data = [{'ticker': ticker, 'qtd': 100, 'data': date(2019, 10, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                      {'ticker': ticker, 'qtd': 100, 'data': date(2019, 10, 12), 'preco': 100, 'aquisicao_via': 'HomeBroker'}]

        other_df = create_testing_dataframe(other_data)

        result = merge_operacoes(df, other_df)

        assert len(result) == len(other_df)

    def test_merge_operacoes_com_ipo(self):
        ticker = random_ticker()

        data = [{'ticker': ticker, 'qtd': 100, 'data': date(2019, 3, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                {'ticker': ticker, 'qtd': 100, 'data': date(2019, 4, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'}]

        other_data = [{'ticker': ticker, 'qtd': 100, 'data': date(2019, 10, 13), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                      {'ticker': ticker, 'qtd': 100, 'data': date(2019, 10, 14), 'preco': 100, 'aquisicao_via': 'HomeBroker'}]
        other_data.extend(data)
        other_df = create_testing_dataframe(other_data)

        data.extend([{'ticker': ticker, 'qtd': -100, 'data': date(2019, 4, 20), 'preco': 200, 'aquisicao_via': 'IPO'}])
        df = create_testing_dataframe(data)

        result = merge_operacoes(df, other_df)

        assert len(result) == (len(df) + 2)

    def test_merge_operacoes_com_ipo_em_uma_data_futura(self):
        ticker = random_ticker()

        data = [{'ticker': ticker, 'qtd': 100, 'data': date(2019, 3, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                {'ticker': ticker, 'qtd': 100, 'data': date(2019, 4, 11), 'preco': 100, 'aquisicao_via': 'HomeBroker'}]

        other_data = [{'ticker': ticker, 'qtd': 100, 'data': date(2019, 10, 13), 'preco': 100, 'aquisicao_via': 'HomeBroker'},
                      {'ticker': ticker, 'qtd': 100, 'data': date(2019, 10, 14), 'preco': 100, 'aquisicao_via': 'HomeBroker'}]
        other_data.extend(data)
        other_df = create_testing_dataframe(other_data)

        data.extend([{'ticker': ticker, 'qtd': -100, 'data': date(2099, 4, 20), 'preco': 200, 'aquisicao_via': 'IPO'}])
        df = create_testing_dataframe(data)

        result = merge_operacoes(df, other_df)

        assert len(result) == (len(df) + 2)

    def test_df_to_csv(self):
        df_original = get_operations()

        df_to_csv(df_original, 'df_to_csv_testing.txt')

        df_lido = get_operations('df_to_csv_testing.txt')
        assert df_lido.equals(df_original)

    def test_calcula_custodia(self):
        from src.dropbox_files import download_dropbox_file
        download_dropbox_file()

        df = get_operations()
        df = df.tail(400)

        data = date.today()
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


    def test_calcula_precos_medios_quando_um_ciclo(self):
        ticker = random_ticker()

        data = [{'ticker': ticker, 'qtd': 100, 'data': date(2019, 4, 20), 'preco': 100},
                {'ticker': ticker, 'qtd': 200, 'data': date(2019, 4, 13), 'preco': 200}]

        df = create_testing_dataframe(data)

        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 14))['valor'] == pytest.approx(200.00, 0.01)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 16))['valor'] == pytest.approx(200.00, 0.01)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 19))['valor'] == pytest.approx(200.00, 0.01)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 20))['valor'] == pytest.approx(166.66, 0.01)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 21))['valor'] == pytest.approx(166.66, 0.01)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 14))['data_primeira_compra'] == date(2019, 4, 13)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 16))['data_primeira_compra'] == date(2019, 4, 13)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 19))['data_primeira_compra'] == date(2019, 4, 13)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 20))['data_primeira_compra'] == date(2019, 4, 13)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 21))['data_primeira_compra'] == date(2019, 4, 13)

    def test_deve_retornar_precos_de_compra_diferentes_quando_varias_operacoes_de_compra_venda_mesmo_mes(self):
        ticker = random_ticker()

        data = [{'ticker': ticker, 'qtd': 100, 'data': date(2019, 4, 10), 'preco': 100},
                {'ticker': ticker, 'qtd': 200, 'data': date(2019, 4, 11), 'preco': 200},
                {'ticker': ticker, 'qtd': 200, 'data': date(2019, 4, 12), 'preco': 200},
                {'ticker': ticker, 'qtd': -100, 'data': date(2019, 4, 13), 'preco': 250},
                {'ticker': ticker, 'qtd': -150, 'data': date(2019, 4, 14), 'preco': 250},
                {'ticker': ticker, 'qtd': 400, 'data': date(2019, 4, 15), 'preco': 400},
                {'ticker': ticker, 'qtd': -250, 'data': date(2019, 4, 16), 'preco': 250}]

        df = create_testing_dataframe(data)

        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 14))['valor'] == pytest.approx(180.00, 0.01)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 16))['valor'] == pytest.approx(315.38, 0.01)


    def test_calcula_precos_medios_quando_varios_tickers_juntos(self):
        ticker = random_ticker()
        ticker2 = random_ticker()

        data = [{'ticker': ticker, 'qtd': 100, 'data': date(2019, 4, 20), 'preco': 100},
                {'ticker': ticker2, 'qtd': 100, 'data': date(2019, 4, 20), 'preco': 100},
                {'ticker': ticker2, 'qtd': 100, 'data': date(2019, 4, 20), 'preco': 200},
                {'ticker': ticker2, 'qtd': 100, 'data': date(2019, 4, 20), 'preco': 300},
                {'ticker': ticker, 'qtd': 200, 'data': date(2019, 4, 13), 'preco': 200}]

        df = create_testing_dataframe(data)

        preco_medio_de_compra = calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 21))
        assert preco_medio_de_compra['valor'] == pytest.approx(166.66, 0.01)
        assert preco_medio_de_compra['data_primeira_compra'] == date(2019, 4, 13)

        preco_medio_de_compra = calcula_preco_medio_de_compra(df, ticker2, date(2019, 4, 21))
        assert preco_medio_de_compra['valor'] == pytest.approx(200.00, 0.01)
        assert preco_medio_de_compra['data_primeira_compra'] == date(2019, 4, 20)

    def test_calcula_precos_medios_quando_varios_ciclo_em_varios_meses(self):
        ticker = random_ticker()
        data = [{'ticker': ticker, 'qtd': 1, 'data': date(2019, 4, 11), 'preco': 5},
                {'ticker': ticker, 'qtd': -1, 'data': date(2019, 4, 12), 'preco': 6},
                {'ticker': ticker, 'qtd': 2, 'data': date(2019, 4, 13), 'preco': 3},
                {'ticker': ticker, 'qtd': -1, 'data': date(2019, 4, 14), 'preco': 2},
                {'ticker': ticker, 'qtd': -1, 'data': date(2019, 4, 15), 'preco': 4},
                {'ticker': ticker, 'qtd': 1, 'data': date(2019, 4, 15), 'preco': 2},
                {'ticker': ticker, 'qtd': 1, 'data': date(2019, 4, 15), 'preco': 3},
                {'ticker': ticker, 'qtd': 1, 'data': date(2019, 4, 15), 'preco': 4},
                {'ticker': ticker, 'qtd': -2, 'data': date(2019, 4, 16), 'preco': 5}]

        df = create_testing_dataframe(data)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 11))['valor'] == pytest.approx(5.0, 0.001)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 13))['valor'] == pytest.approx(3.0, 0.001)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 14))['valor'] == pytest.approx(3.0, 0.001)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 15))['valor'] == pytest.approx(3.0, 0.001)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 20))['valor'] == pytest.approx(3.0, 0.001)

        ticker = random_ticker()
        data = [{'ticker': ticker, 'qtd': 100, 'data': date(2019, 4, 11), 'preco': 200},
                {'ticker': ticker, 'qtd': -100, 'data': date(2019, 4, 12), 'preco': 200},
                {'ticker': ticker, 'qtd': 100, 'data': date(2019, 4, 13), 'preco': 300},
                {'ticker': ticker, 'qtd': 100, 'data': date(2019, 4, 14), 'preco': 400},
                {'ticker': ticker, 'qtd': -200, 'data': date(2019, 4, 15), 'preco': 500},
                {'ticker': ticker, 'qtd': 2, 'data': date(2019, 4, 16), 'preco': 5},
                {'ticker': ticker, 'qtd': -1, 'data': date(2019, 4, 16), 'preco': 1},
                {'ticker': ticker, 'qtd': 3, 'data': date(2019, 4, 17), 'preco': 2},
                {'ticker': ticker, 'qtd': 1, 'data': date(2019, 4, 17), 'preco': 20}]

        df = create_testing_dataframe(data)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 15))['valor'] == pytest.approx(350.0, 0.001)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 16))['valor'] == pytest.approx(5.0, 0.001)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 17))['valor'] == pytest.approx(6.2, 0.001)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 11))['data_primeira_compra'] == date(2019, 4, 11)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 12))['data_primeira_compra'] == date(2019, 4, 11)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 15))['data_primeira_compra'] == date(2019, 4, 13)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 16))['data_primeira_compra'] == date(2019, 4, 16)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 17))['data_primeira_compra'] == date(2019, 4, 16)


    def test_calcula_precos_medios_quando_operacoes_no_mesmo_dia_estao_fora_de_ordem(self):
        # dentro de um mesmo dia, nao existe a informacao de horas.
        # logo, nao há garantia de que as operacoes ocorreram na ordem informada (dentro um mesmo dia)

        ticker = random_ticker()

        data = [{'ticker': ticker, 'qtd': 100,  'data': date(2019, 4, 11), 'preco': 100},
                {'ticker': ticker, 'qtd': -100, 'data': date(2019, 4, 12), 'preco': 200},
                {'ticker': ticker, 'qtd': -200, 'data': date(2019, 4, 13), 'preco': 500},
                {'ticker': ticker, 'qtd': 100,  'data': date(2019, 4, 13), 'preco': 300},
                {'ticker': ticker, 'qtd': 100,  'data': date(2019, 4, 13), 'preco': 400},
                {'ticker': ticker, 'qtd': -1,   'data': date(2019, 4, 15), 'preco': 1},
                {'ticker': ticker, 'qtd': 2,    'data': date(2019, 4, 15), 'preco': 5},
                {'ticker': ticker, 'qtd': 3,    'data': date(2019, 4, 15), 'preco': 2},
                {'ticker': ticker, 'qtd': 1,    'data': date(2019, 4, 16), 'preco': 2}]

        df = create_testing_dataframe(data)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 11))['valor'] == pytest.approx(100.0, 0.001)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 13))['valor'] == pytest.approx(350.0, 0.001)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 17))['valor'] == pytest.approx(2.96, 0.001)
        assert calcula_preco_medio_de_compra(df, ticker, date(2019, 4, 17))['data_primeira_compra'] == date(2019, 4, 15)

    def test_deve_verificar_se_todos_os_tickers_possuem_tipo_com_sucesso(self):
        data = [{'ticker': 'CMIN3', 'qtd': -1, 'data': date(2019, 4, 12), 'preco': 6},
                {'ticker': 'GRLV11', 'qtd': 2, 'data': date(2019, 4, 13), 'preco': 3}]

        df = create_testing_dataframe(data)
        check_tipo_ticker(df)

    def test_deve_lancar_excecao_se_algum_ticker_nao_possui_tipo(self):
        data = [{'ticker': 'error', 'qtd': -1, 'data': date(2019, 4, 12), 'preco': 6},
                {'ticker': 'GRLV11', 'qtd': 2, 'data': date(2019, 4, 13), 'preco': 3}]

        df = create_testing_dataframe(data)
        with pytest.raises(Exception):
            check_tipo_ticker(df)
