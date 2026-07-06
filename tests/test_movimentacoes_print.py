import datetime

from src.movimentacoes_print import parse_data, validar_formato


class TestParseData:

    def test_parse_data_com_ano_com_4_digitos(self):
        assert parse_data('02/06/2025') == datetime.date(2025, 6, 2)

    def test_parse_data_com_ano_com_2_digitos(self):
        assert parse_data('02/06/25') == datetime.date(2025, 6, 2)

    def test_parse_data_invalida_retorna_none(self):
        assert parse_data('31/13/2025') is None
        assert parse_data('nao e uma data') is None


class TestValidarFormato:

    def registro_valido(self, **overrides):
        base = {'ticker': 'ITRI11', 'tipo': 'Venda', 'qtd': 550, 'data': '02/06/2025', 'preco': 81.2, 'valor': 44660}
        base.update(overrides)
        return base

    def test_registro_valido_passa(self):
        ok, motivo = validar_formato(self.registro_valido())
        assert ok is True
        assert motivo is None

    def test_ticker_fora_do_padrao_falha(self):
        ok, motivo = validar_formato(self.registro_valido(ticker='itri11'))
        assert ok is False
        assert 'ticker' in motivo

    def test_data_invalida_falha(self):
        ok, motivo = validar_formato(self.registro_valido(data='31/13/2025'))
        assert ok is False
        assert 'data' in motivo

    def test_qtd_zero_falha(self):
        ok, motivo = validar_formato(self.registro_valido(qtd=0))
        assert ok is False
        assert 'qtd' in motivo

    def test_qtd_nao_numerica_falha(self):
        ok, motivo = validar_formato(self.registro_valido(qtd='abc'))
        assert ok is False
        assert 'qtd' in motivo

    def test_preco_negativo_falha(self):
        ok, motivo = validar_formato(self.registro_valido(preco=-1))
        assert ok is False
        assert 'preco' in motivo

    def test_valor_incompativel_com_qtd_vezes_preco_falha(self):
        ok, motivo = validar_formato(self.registro_valido(valor=999999))
        assert ok is False
        assert 'valor' in motivo

    def test_valor_ausente_nao_falha(self):
        registro = self.registro_valido()
        del registro['valor']
        ok, motivo = validar_formato(registro)
        assert ok is True
        assert motivo is None
