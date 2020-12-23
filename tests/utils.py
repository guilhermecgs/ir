import sys
import pandas as pd
from bs4 import BeautifulSoup
from src.driver_selenium import ChromeDriver

from src.stuff import colunas_obrigatorias, calcula_valor


def create_testing_dataframe(data):
    for row in data:
        for column in colunas_obrigatorias():
            if column not in row:
                row[column] = None

    if len(data):
        df = pd.DataFrame(data)
        df['qtd_ajustada'] = df['qtd']
        df['qtd'] = df.apply(lambda row: abs(row.qtd), axis=1)
        df['valor'] = df.apply(lambda row: calcula_valor(row.qtd, row.preco), axis=1)
    else:
        df = pd.DataFrame(columns=colunas_obrigatorias())

    return df


this = sys.modules[__name__]
this.__cache__ = []


def get_random_opcoes_tickers():
    if not len(this.__cache__):
        driver = None
        driver = ChromeDriver()
        driver.get('https://opcoes.net.br/opcoes/bovespa/PETR4')

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        table = soup.find('table', {'id': 'tblListaOpc'})

        df = pd.read_html(str(table), decimal=',', thousands='.')[0]

        this.__cache__ = df['Ticker']['Ticker'].tolist()

    return this.__cache__
