from src.preco_atual import busca_preco_atual
from src.crawler_advfn import busca_parametros


class TestBuscaPrecoAtual():

    def test_busca_preco_atual(self):
        busca_parametros.clear_cache()
        assert busca_preco_atual('INVALID') is None
        assert type(busca_preco_atual('ITSA4')) is float
        assert type(busca_preco_atual('VRTA11')) is float
        assert type(busca_preco_atual('BOVA11')) is float
        assert type(busca_preco_atual('MAXR11')) is float
        assert type(busca_preco_atual('MELI34')) is float


