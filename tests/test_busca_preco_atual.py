from src.preco_atual import busca_preco_atual


class TestBuscaPrecoAtual():

    def test_busca_preco_atual(self):
        assert busca_preco_atual('INVALID') is None
        assert type(busca_preco_atual('ITSA4')) is float
        assert type(busca_preco_atual('VRTA11')) is float
        assert type(busca_preco_atual('BOVA11')) is float

