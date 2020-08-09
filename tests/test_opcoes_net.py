import unittest.mock as mock
from unittest import TestCase


from src import crawler_opcoes_net
from src.crawler_opcoes_net import eh_tipo_opcao


class TestCrawlerAdvfn(TestCase):

    def __reset_cache(self):
        crawler_opcoes_net.cache = {}

    def test_deve_buscar_apenas_uma_vez_em_opcoes_net(self):
        self.__reset_cache()

        return_value = {'eh_tipo_opcao': True}
        with mock.patch.object(crawler_opcoes_net, '__recupera_informacoes', return_value=return_value) as method:
            eh_tipo_opcao('ACAO11')
            eh_tipo_opcao('ACAO11')
            eh_tipo_opcao('ACAO11')
            eh_tipo_opcao('ACAO12')
            eh_tipo_opcao('ACAO12')
            eh_tipo_opcao('ACAO12')
            assert method.call_count == 2

    def test_busca_tipo_ticker(self):
        assert eh_tipo_opcao('INVALID') is False
        assert eh_tipo_opcao('ABEVH222') == True
        assert eh_tipo_opcao('ABEVT40') == True
        assert eh_tipo_opcao('ABEVT45') == True
        assert eh_tipo_opcao('AZULG525') == True
        assert eh_tipo_opcao('PETRG229') == True
        assert eh_tipo_opcao('IRBRH115') == True
        assert eh_tipo_opcao('ABEVS41') == True
        assert eh_tipo_opcao('MRFGH18') == True
        assert eh_tipo_opcao('CMIGG14') == True
        assert eh_tipo_opcao('COGNG7') == True
