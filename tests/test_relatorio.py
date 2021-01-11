import datetime
from unittest import TestCase

from src.calculo_ir import CalculoIr
from src.relatorio import relatorio_html, relatorio_txt
from src.stuff import get_operations, calcula_custodia
from tests.utils import create_testing_dataframe, OPERACOES_DE_TESTE
from src.dropbox_files import OPERATIONS_FILEPATH

class TestRelatorio(TestCase):

    def test_relatorio_html(self):
        data = [{'ticker': 'MAXR11', 'qtd': 100, 'data': datetime.date(2019, 3, 11), 'preco': 100,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'PETR4', 'qtd': 100, 'data': datetime.date(2019, 4, 11), 'preco': 100,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'XPLG11', 'qtd': 100, 'data': datetime.date(2019, 4, 12), 'preco': 200,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'XPLG11', 'qtd': -50, 'data': datetime.date(2019, 5, 12), 'preco': 220,
                 'aquisicao_via': 'HomeBroker'}]

        df = create_testing_dataframe(data)

        custodia = calcula_custodia(df)
        calculo_ir = CalculoIr(df=df)
        calculo_ir.calcula()

        from py_w3c.validators.html.validator import HTMLValidator

        assert HTMLValidator().validate_fragment(relatorio_html(custodia, calculo_ir, datetime.date.today(), False))

    def test_relatorio_txt(self):
        from src.dropbox_files import download_dropbox_file
        download_dropbox_file(OPERACOES_DE_TESTE)

        df = get_operations(OPERACOES_DE_TESTE)
        assert len(df.count()) > 0
        df = df.tail(60)

        custodia = calcula_custodia(df)
        calculo_ir = CalculoIr(df=df)
        calculo_ir.calcula()

        with open("relatorio_teste.txt", "w") as relatorio:
            relatorio.write(relatorio_txt(custodia, calculo_ir, datetime.date.today(), False))

