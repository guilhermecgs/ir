import pytest
from src.crawler_yahoo import busca_preco_atual

import warnings
warnings.filterwarnings(action="ignore", message="unclosed",
                         category=ResourceWarning)


class TestCrawlerYahoo():

    def test_get_ticker_price(self):
        busca_preco_atual.clear_cache()

        with pytest.raises(Exception):
            busca_preco_atual('invalid')

        sdil11 = busca_preco_atual('SDIL11')
        maxr11 = busca_preco_atual('MAXR11')
        itsa4 = busca_preco_atual('ITSA4')
        vrta11 = busca_preco_atual('VRTA11')
        bova11 = busca_preco_atual('BOVA11')

        assert type(sdil11) is float
        assert type(maxr11) is float
        assert type(itsa4) is float
        assert type(vrta11) is float
        assert type(bova11) is float
