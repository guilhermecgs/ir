import pandas as pd
import datetime
from src.importador_negociacao_b3 import ImportadorNegociacaoB3

class TestImportadorNegociacaoB3():

    def test_busca_trades(self):
        importador = ImportadorNegociacaoB3()
        resultado = importador.busca_trades('tests/exemplos')
        
        esperado = [
            {'data':  datetime.date(2023, 1, 1), 'operacao': 'Venda', 'ticker': 'VEND1', 'qtd': 1600, 'preco': 1.44, 'valor': 2304, 'qtd_ajustada': -1600, 'taxas': 0, 'aquisicao_via': 'HomeBroker'},
            {'data':  datetime.date(2023, 1, 2), 'operacao': 'Compra', 'ticker': 'COMP1', 'qtd': 100, 'preco': 27.19, 'valor': 2719, 'qtd_ajustada': 100, 'taxas': 0, 'aquisicao_via': 'HomeBroker'},
        ]
        assert esperado == resultado.to_dict('records')