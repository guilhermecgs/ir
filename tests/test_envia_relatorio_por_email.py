from unittest import TestCase
import datetime

from src.calculo_ir import CalculoIr
from src.relatorio import relatorio_html
from src.stuff import calcula_custodia
from src.envia_relatorio_por_email import envia_relatorio_txt_por_email, envia_relatorio_html_por_email
from tests.utils import create_testing_dataframe


class TestEnvia_relatorio_por_email(TestCase):

    def test_envia_relatorio_txt_por_email(self):
        assert envia_relatorio_txt_por_email('assunto - teste unitário', 'relatório')

    def test_envia_relatorio_html_por_email(self):
        data = [{'ticker': 'MAXR11', 'qtd': 100, 'data': datetime.date(2019, 3, 11), 'preco': 100,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'PETR4', 'qtd': 100, 'data': datetime.date(2019, 4, 11), 'preco': 100,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'XPLG11', 'qtd': 100, 'data': datetime.date(2019, 4, 12), 'preco': 200,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'XPLG11', 'qtd': -50, 'data': datetime.date(2019, 5, 12), 'preco': 220,
                 'aquisicao_via': 'HomeBroker'}]

        df = create_testing_dataframe(data)

        calcula_custodia(df)
        calculo_ir = CalculoIr(df=df)
        calculo_ir.calcula()

        assert envia_relatorio_html_por_email('assunto - teste unitário', relatorio_html(calculo_ir))