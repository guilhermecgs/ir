import unittest
from unittest.mock import patch
from src import crawler_b3_etfs
from src.crawler_b3_etfs import e_tipo_etf


class TestCrawlerEtfsB3(unittest.TestCase):

    def __reset_etfs(self):
        crawler_b3_etfs.etfs = None

    @patch('src.crawler_b3_etfs.__busca_etfs_na_b3')
    def test_deve_buscar_etfs_apenas_uma_vez_na_b3(self, busca_etfs_na_b3):
        self.__reset_etfs()
        busca_etfs_na_b3.return_value = ['BOVA', 'DIVO']
        assert e_tipo_etf('BOVA11')
        assert e_tipo_etf('BOVA11')
        assert e_tipo_etf('DIVO11')
        assert busca_etfs_na_b3.call_count == 1

    def test_crawler(self):
        self.__reset_etfs()
        assert e_tipo_etf('BOVA11')
        assert e_tipo_etf('bova11')
        assert e_tipo_etf('DIVO11')
        assert e_tipo_etf('ISUS11')
        assert e_tipo_etf('SMAC11')
        assert e_tipo_etf('SPXI11')
        assert not e_tipo_etf('ITSA4')
        assert not e_tipo_etf('VRTA11')
        assert not e_tipo_etf('invalid')

