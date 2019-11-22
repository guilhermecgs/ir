import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.tipo_ticker import TipoTicker
from src.stuff import tipo_ticker, vendas_no_mes


class CalculoIr():
    df: pd.DataFrame
    vendas: dict = dict()
    prejuizo_acumulado: dict = {}
    datas: list = []

    def __init__(self, df):
        self.df = df

    def calcula(self):
        hoje = datetime.datetime.now().date()

        data = data_inicial = self.df['data'].min() + relativedelta(months=-1)

        while data < hoje:
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

        pass

    def calcula_prejuizo_acumulado(self, data, tipo):
        prejuizo_acumulado = self.calcula_prejuizo_por_tipo(data, tipo)

        if self.__tem_prejuizo_no_mes_anterior(tipo, data):
            prejuizo_acumulado = prejuizo_acumulado + self.__prejuizo_no_mes_anterior(tipo, data)

        return prejuizo_acumulado

    def calcula_ir_a_pagar_no_mes(self, data):
        ir_a_pagar = 0.0
        for tipo in TipoTicker:
            prejuizo_acumulado = self.calcula_prejuizo_acumulado(data, tipo)
            ir_a_pagar += self.calcula_ir_a_pagar(prejuizo_acumulado, tipo)
        return ir_a_pagar

    def calcula_ir_a_pagar(self, lucro, tipo):
        if lucro > 0:
            if tipo == TipoTicker.ACAO:
                return lucro * 0.2
            if tipo == TipoTicker.ETF:
                return lucro * 0.15
            if tipo == TipoTicker.FII:
                return lucro * 0.2
        return 0.0

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
        return str(data.month) + '_' + str(data.year)

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

    def get_vendas_no_mes_por_tipo(self, data):
        return self.vendas[self.__get_date_key__(data)]

    def possui_vendas_no_mes(self, data):
        for tipo in TipoTicker:
            if len(self.vendas[self.__get_date_key__(data)][tipo]):
                return True

        return False
