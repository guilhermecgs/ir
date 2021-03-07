import datetime
import calendar
import pandas as pd
from dateutil.relativedelta import relativedelta

from src.tipo_ticker import TipoTicker
from src.stuff import tipo_ticker, vendas_no_mes


class CalculoIr():
    df: pd.DataFrame
    vendas: dict = dict()
    prejuizo_acumulado: dict = {}
    datas: list = []
    mes_do_relatorio : str

    def __init__(self, df):
        self.df = df

    def calcula(self):
        hoje = datetime.datetime.now().date()

        data_inicial = self.df['data'].min() + relativedelta(months=-1)
        data = data_inicial = datetime.date(data_inicial.year, data_inicial.month, 1)
        data_final = hoje + relativedelta(months=-1)
        data_final = datetime.date(data_final.year, data_final.month, calendar.monthrange(data_final.year,data_final.month)[1])

        self.mes_do_relatorio = self.__get_date_key__(data_final)

        while data <= data_final:
            self.datas.append(data)
            data = data + relativedelta(months=1)

        self.prejuizo_acumulado = {}
        for tipo in TipoTicker:
            self.__seta_prejuizo_acumulado(data_inicial, tipo, 0.0)

        for index, data in enumerate(self.datas):
            self.__seta_vendas_no_mes(data, vendas_no_mes(self.df, data.year, data.month))

            for tipo in TipoTicker:
                prejuizo_acumulado = self.calcula_prejuizo_acumulado(data, tipo)
                self.__seta_prejuizo_acumulado(data, tipo, prejuizo_acumulado)

    def calcula_prejuizo_acumulado(self, data, tipo):
        prejuizo_acumulado = self.calcula_prejuizo_por_tipo(data, tipo)

        if self.__tem_prejuizo_no_mes_anterior(tipo, data):
            prejuizo_acumulado = prejuizo_acumulado + self.__prejuizo_no_mes_anterior(tipo, data)

        return prejuizo_acumulado

    def calcula_ir_a_pagar_no_mes(self, data):
        ir_a_pagar = 0.0
        for tipo in TipoTicker:
            prejuizo_acumulado = self.calcula_prejuizo_acumulado(data, tipo)
            ir_a_pagar += calcula_ir_a_pagar(prejuizo_acumulado, tipo,
                                             self.total_vendido_no_mes_por_tipo(data)[TipoTicker.ACAO])
        return ir_a_pagar

    def calcula_dedo_duro_no_mes(self, data):
        porcentagem_dedo_duro = 0.005 / 100.0
        return sum(operacao_de_venda['preco_medio_venda'] * operacao_de_venda['qtd_vendida']
                   for operacao_de_venda in vendas_no_mes(self.df, data.year, data.month)) * porcentagem_dedo_duro

    def calcula_prejuizo_por_tipo(self, data, tipo):
        return sum([venda['resultado_apurado'] for venda in self.vendas[self.__get_date_key__(data)][tipo]])

    def __tem_prejuizo_no_mes_anterior(self, tipo, data):
        if self.__prejuizo_no_mes_anterior(tipo, data) < 0:
            return True
        return False

    def __prejuizo_no_mes_anterior(self, tipo, data):
        mes_anterior = self.__get_date_key__(data + relativedelta(months=-1))
        if mes_anterior in self.prejuizo_acumulado:
            return self.prejuizo_acumulado[mes_anterior][tipo]
        return 0.0

    def __get_date_key__(self, data):
        return str(data.month) + '/' + str(data.year)

    def __seta_prejuizo_acumulado(self, data, tipo, prejuizo):
        if not self.__get_date_key__(data) in self.prejuizo_acumulado:
            self.prejuizo_acumulado[self.__get_date_key__(data)] = {}

        self.prejuizo_acumulado[self.__get_date_key__(data)][tipo] = prejuizo

    def __seta_vendas_no_mes(self, data, vendas_no_mes):
        self.vendas[self.__get_date_key__(data)] = {}

        for tipo in TipoTicker:
            self.vendas[self.__get_date_key__(data)][tipo] = []

        for venda in vendas_no_mes:
            ticker = venda['ticker']
            self.vendas[self.__get_date_key__(data)][tipo_ticker(ticker)].append(venda)

    def total_vendido_no_mes_por_tipo(self, data):
        total_vendido_no_mes = {}

        for tipo in self.vendas[self.__get_date_key__(data)]:
            total_vendido_no_mes[tipo] = sum([venda['qtd_vendida'] * venda['preco_medio_venda']
                                        for venda in self.vendas[self.__get_date_key__(data)][tipo]])
        return total_vendido_no_mes

    def vendas_no_mes_por_tipo(self, data):
        return self.vendas[self.__get_date_key__(data)]

    def possui_vendas_no_mes(self, data):
        for tipo in TipoTicker:
            if len(self.vendas[self.__get_date_key__(data)][tipo]):
                return True

        return False


def calcula_ir_a_pagar(lucro, tipo, vendas_acoes_no_mes=None):
    if lucro > 0:
        if tipo == TipoTicker.ACAO:
            if vendas_acoes_no_mes > 20000.0:
                return lucro * 0.15
            else:
                return 0.0
        if tipo == TipoTicker.BDR \
                or tipo == TipoTicker.ETF \
                or tipo == TipoTicker.FUTURO \
                or tipo == TipoTicker.OPCAO:
            return lucro * 0.15
        if tipo == TipoTicker.FII or tipo == TipoTicker.FIP:
            return lucro * 0.2
        if tipo == TipoTicker.FIPIE:
            return 0.0
    return 0.0


