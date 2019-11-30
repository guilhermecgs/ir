from unittest import TestCase
import datetime
from tests.test_stuff import create_testing_dataframe
from src.envia_relatorio_por_email import envia_relatorio_txt_por_email, envia_relatorio_html_por_email


class TestEnvia_relatorio_por_email(TestCase):

    def test_envia_relatorio_txt_por_email(self):
        assert envia_relatorio_txt_por_email('assunto - teste unitário', 'relatório')

    def test_envia_relatorio_html_por_email(self):
        data = [{'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 3, 11), 'preco': 100,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'gcgs', 'qtd': 100, 'data': datetime.date(2019, 4, 11), 'preco': 100,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'gcgs', 'qtd': -100, 'data': datetime.date(2019, 4, 12), 'preco': 200,
                 'aquisicao_via': 'HomeBroker'}]

        df = create_testing_dataframe(data)
        assert envia_relatorio_html_por_email('assunto - teste unitário', df.to_html())