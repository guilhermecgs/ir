import datetime

import pytest

from tests.utils import create_testing_dataframe
from src.stuff import calcula_custodia
from src.calculo_ir import CalculoIr
from src.tipo_ticker import TipoTicker
from src.calculo_ir import calcula_ir_a_pagar


class TestCalculoIr():

    def test_acoes_deve_ter_percentual_de_15_perc(self):
        assert calcula_ir_a_pagar(25000, TipoTicker.ACAO, 100000) == 3750.0

    def test_acoes_isencao_ate_20_mil_de_vendas_no_mes(self):
        assert calcula_ir_a_pagar(15000, TipoTicker.ACAO, 15000) == 0.0
        assert calcula_ir_a_pagar(15000, TipoTicker.ACAO, 30000) == 2250.0

    @pytest.mark.parametrize("tipo_ticker",
                             filter(lambda tipo: tipo not in (TipoTicker.ACAO, TipoTicker.FIPIE),
                                                   [tipo for tipo in TipoTicker if tipo]))
    def test_apenas_acoes_possuem_isencao_de_vendas_ate_20_mil(self, tipo_ticker):
        assert calcula_ir_a_pagar(10000, tipo_ticker, 15000) > 0.0

    def test_fii_deve_ter_percentual_de_20_perc(self):
        assert calcula_ir_a_pagar(25000, TipoTicker.FII) == 5000.0

    def test_fipe_deve_ter_percentual_de_20_perc(self):
        assert calcula_ir_a_pagar(25000, TipoTicker.FIP) == 5000.0

    def test_bdr_deve_ter_percentual_de_15_perc(self):
        assert calcula_ir_a_pagar(25000, TipoTicker.BDR) == 3750.0

    @pytest.mark.parametrize("tipo_ticker", [tipo for tipo in TipoTicker])
    def test_deve_ser_zero_se_nao_tiver_lucro(self, tipo_ticker):
        assert calcula_ir_a_pagar(0, tipo_ticker) == 0.0

    def test_etf_deve_ter_percentual_de_15_perc(self):
        assert calcula_ir_a_pagar(25000, TipoTicker.ETF) == 3750.0

    def test_futuro_deve_ter_percentual_de_15_perc(self):
        assert calcula_ir_a_pagar(25000, TipoTicker.FUTURO) == 3750.0

    def test_opcao_deve_ter_percentual_de_15_perc(self):
        assert calcula_ir_a_pagar(25000, TipoTicker.OPCAO) == 3750.0

    def test_tipos_isentos_devem_ter_imposto_zero(self):
        assert calcula_ir_a_pagar(25000, TipoTicker.FIPIE) == 0.0

    # TODO:
    # deve considerar prejuizo acumulado para acoes, etf, etc, quase tudo
    # deve considerar prejuizo acumulado apenas por mesmo tipo. Ex: tipos de (fii), (acoes, futuros, opcoes), (efts?)
    # calculo ir deve marcar flag vendas no mes
    # deve calcular prejuizo_por_tipo para um mes e tipo.
    # deve considerar meses desde a primeira compra ate o dia atual
    # deve testar todos os metodos publicos
