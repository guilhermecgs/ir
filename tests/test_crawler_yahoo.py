import pytest
from src.crawler_yahoo import busca_preco_atual_yahoo

import warnings
warnings.filterwarnings(action="ignore", message="unclosed",
                         category=ResourceWarning)


class TestCrawlerYahoo():

    def test_get_ticker_price(self):
        busca_preco_atual_yahoo.clear_cache()

        assert busca_preco_atual_yahoo('invalid') is None

        sdil11 = busca_preco_atual_yahoo('SDIL11')
        itsa4 = busca_preco_atual_yahoo('ITSA4')
        vrta11 = busca_preco_atual_yahoo('VRTA11')

        assert type(sdil11) is float
        assert type(itsa4) is float
        assert type(vrta11) is float
