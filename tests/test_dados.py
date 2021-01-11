from unittest import TestCase
from src.dados import get_data, ticker_nome, ticker_cnpj, ticker_data

class TestDados(TestCase):

    def test_001(self):
        assert ticker_nome('WEGE3') == 'WEG S.A.'
        assert ticker_cnpj('XPML11') == '28.757.546/0001-00'
        assert ticker_data('XPML11','nome_adm') == 'BTG PACTUAL SERVIÇOS FINANCEIROS S/A DTVM'
        
        