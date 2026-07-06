import datetime
import json

from src.movimentacoes_print import (
    parse_data,
    validar_formato,
    chave_duplicidade,
    parse_arquivo_operacoes,
    formatar_linha_txt,
    classificar_candidatos,
    executar_classificacao,
)


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


class TestChaveDuplicidade:

    def test_mesma_movimentacao_gera_mesma_chave_mesmo_com_formatacao_diferente(self):
        chave1 = chave_duplicidade('ITRI11', 'Venda', 550, '02/06/2025', 81.2)
        chave2 = chave_duplicidade('ITRI11', 'Venda', 550.0, '02/06/25', 81.200)
        assert chave1 == chave2

    def test_movimentacoes_diferentes_geram_chaves_diferentes(self):
        chave1 = chave_duplicidade('ITRI11', 'Venda', 550, '02/06/2025', 81.2)
        chave2 = chave_duplicidade('ITRI11', 'Venda', 600, '02/06/2025', 81.2)
        assert chave1 != chave2


class TestParseArquivoOperacoes:

    def test_parse_arquivo_com_linhas_reais(self, tmp_path):
        arquivo = tmp_path / 'export_operacoes.txt'
        arquivo.write_text(
            'ITRI11\tVenda\t550.000\t02/06/25\t81.200\t0.000\tHomeBroker\n'
            'BBAS3\tCompra\t1500.000\t16/05/25\t25.700\t0.000\tHomeBroker\n'
        )

        chaves = parse_arquivo_operacoes(str(arquivo))

        assert chave_duplicidade('ITRI11', 'Venda', 550, '02/06/25', 81.2) in chaves
        assert chave_duplicidade('BBAS3', 'Compra', 1500, '16/05/25', 25.7) in chaves
        assert len(chaves) == 2

    def test_parse_arquivo_vazio(self, tmp_path):
        arquivo = tmp_path / 'export_operacoes.txt'
        arquivo.write_text('')

        assert parse_arquivo_operacoes(str(arquivo)) == []


class TestFormatarLinhaTxt:

    def test_formata_linha_igual_ao_arquivo_real(self):
        registro = {'ticker': 'ITRI11', 'tipo': 'Venda', 'qtd': 550, 'data': '02/06/25', 'preco': 81.2}
        assert formatar_linha_txt(registro) == 'ITRI11\tVenda\t550.000\t02/06/25\t81.200\t0.000\tHomeBroker'


class TestClassificarCandidatos:

    def test_candidato_valido_e_novo_fica_pronto(self):
        candidatos = [{'ticker': 'BBAS3', 'tipo': 'Compra', 'qtd': 1500, 'data': '16/05/25', 'preco': 25.7}]

        resultado = classificar_candidatos(candidatos, chaves_existentes=[])

        assert resultado[0]['categoria'] == 'pronto'
        assert resultado[0]['linha_txt'] == 'BBAS3\tCompra\t1500.000\t16/05/25\t25.700\t0.000\tHomeBroker'
        assert resultado[0]['motivo'] is None

    def test_candidato_com_formato_invalido_vira_observacao(self):
        candidatos = [{'ticker': 'invalido', 'tipo': 'Compra', 'qtd': 100, 'data': '16/05/25', 'preco': 10}]

        resultado = classificar_candidatos(candidatos, chaves_existentes=[])

        assert resultado[0]['categoria'] == 'observacao'
        assert 'ticker' in resultado[0]['motivo']
        assert resultado[0]['linha_txt'] is None

    def test_tipo_fora_do_padrao_vira_observacao_com_campos_preservados(self):
        candidatos = [{'ticker': 'BBAS3', 'tipo': 'Desdobramento', 'qtd': 100, 'data': '16/05/25', 'preco': 10}]

        resultado = classificar_candidatos(candidatos, chaves_existentes=[])

        assert resultado[0]['categoria'] == 'observacao'
        assert 'Desdobramento' in resultado[0]['motivo']
        assert resultado[0]['ticker'] == 'BBAS3'
        assert resultado[0]['linha_txt'] is None

    def test_candidato_duplicado_no_arquivo_existente_vira_observacao(self):
        candidatos = [{'ticker': 'ITRI11', 'tipo': 'Venda', 'qtd': 550, 'data': '02/06/25', 'preco': 81.2}]
        chaves_existentes = [chave_duplicidade('ITRI11', 'Venda', 550, '02/06/25', 81.2)]

        resultado = classificar_candidatos(candidatos, chaves_existentes)

        assert resultado[0]['categoria'] == 'observacao'
        assert 'ja existe' in resultado[0]['motivo']

    def test_dois_candidatos_identicos_no_mesmo_lote_segundo_vira_observacao(self):
        candidato = {'ticker': 'BBAS3', 'tipo': 'Compra', 'qtd': 1500, 'data': '16/05/25', 'preco': 25.7}
        candidatos = [dict(candidato), dict(candidato)]

        resultado = classificar_candidatos(candidatos, chaves_existentes=[])

        assert resultado[0]['categoria'] == 'pronto'
        assert resultado[1]['categoria'] == 'observacao'
        assert 'ja existe' in resultado[1]['motivo']


class TestExecutarClassificacao:

    def test_executar_classificacao_le_arquivos_e_retorna_json(self, tmp_path):
        operacoes = tmp_path / 'export_operacoes.txt'
        operacoes.write_text('ITRI11\tVenda\t550.000\t02/06/25\t81.200\t0.000\tHomeBroker\n')

        candidatos_path = tmp_path / 'candidatos.json'
        candidatos_path.write_text(json.dumps([
            {'ticker': 'ITRI11', 'tipo': 'Venda', 'qtd': 550, 'data': '02/06/25', 'preco': 81.2},
            {'ticker': 'BBAS3', 'tipo': 'Compra', 'qtd': 1500, 'data': '16/05/25', 'preco': 25.7},
        ]))

        resultado_json = executar_classificacao(str(candidatos_path), str(operacoes))
        resultado = json.loads(resultado_json)

        assert resultado[0]['categoria'] == 'observacao'
        assert 'ja existe' in resultado[0]['motivo']
        assert resultado[1]['categoria'] == 'pronto'
        assert resultado[1]['linha_txt'] == 'BBAS3\tCompra\t1500.000\t16/05/25\t25.700\t0.000\tHomeBroker'
