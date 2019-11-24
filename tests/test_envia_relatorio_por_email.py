from unittest import TestCase
from src.envia_relatorio_por_email import envia_relatorio_txt_por_email


class TestEnvia_relatorio_por_email(TestCase):

    def test_envia_relatorio_por_email(self):
        assert envia_relatorio_txt_por_email('assunto - teste unitário', 'relatório')
