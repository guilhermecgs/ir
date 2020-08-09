import sys
import logging
from bs4 import BeautifulSoup

import pandas as pd
from selenium import webdriver
import chromedriver_binary  # do not remove

from src.tipo_ticker import TipoTicker
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


this = sys.modules[__name__]
this.cache = {}


logger = logging.getLogger()
logger.setLevel(logging.ERROR)


class CrawlerAdvfn():

    def __init__(self):
        from src.driver_selenium import ChromeDriver
        self.driver = ChromeDriver()

    def __get_url(self, ticker):
        return 'https://br.advfn.com/bolsa-de-valores/bmf/{ticker}/cotacao'.format(ticker=ticker)

    def busca_preco_atual(self, ticker):
        ticker = ticker.lower()

        if ticker in this.cache:
            return this.cache[ticker]['preco_atual']
        else:
            try:
                this.cache[ticker] = self.__recupera_informacoes(ticker)

                return this.cache[ticker]['preco_atual']

            except Exception as ex:
                logger.exception('ticker: {ticker}'.format(ticker=ticker), ex)
                return None

    def busca_tipo_ticker(self, ticker):
        ticker = ticker.lower()

        if ticker in this.cache:
            return this.cache[ticker]['tipo_ticker']
        else:
            try:
                this.cache[ticker] = self.__recupera_informacoes(ticker)

                return this.cache[ticker]['tipo_ticker']

            except Exception as ex:
                logger.exception('ticker: {ticker}'.format(ticker=ticker), ex)
                return None

    def __recupera_informacoes(self, ticker):
        self.driver.get(self.__get_url(ticker))

        preco_atual = self.__recupera_preco_atual()

        tipo_ticker = self.__recupera_tipo_ticker()

        return {'tipo_ticker': tipo_ticker, 'preco_atual': preco_atual}

    def __recupera_preco_atual(self):
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, 'quoteElementPiece10')))
        preco_atual = float(self.driver.find_element_by_id('quoteElementPiece10').text
                            .replace('.', '').replace(',', '.'))
        return preco_atual

    def __recupera_tipo_ticker(self):
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, 'quoteElementPiece5')))
        tipo = self.driver.find_element_by_id('quoteElementPiece5').text.lower()

        if tipo == 'futuro':
            return TipoTicker.FUTURO

        if tipo == 'opção':
            return TipoTicker.OPCAO

        if tipo == 'preferencial' or tipo == 'ordinária':
            return TipoTicker.ACAO

        if tipo == 'fundo':
            if self.__fundo_eh_fii():
                return TipoTicker.FII

            if self.__fundo_eh_etf():
                return TipoTicker.ETF

        return None

    def __fundo_eh_etf(self):
        if 'Exchange Traded Fund' in self.driver.page_source:
            return True
        return False

    def __fundo_eh_fii(self):
        try:
            nome = self.driver.find_elements_by_class_name("page-name-h1")[0].text.lower()
            dividendos = self.__converte_tabela_dividendos_para_df();

            if 'FII' in nome.upper() and len(dividendos):
                return True
            else:
                return False
        except:
            return False

    def __converte_tabela_dividendos_para_df(self):
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            table = soup.find('table', {'id': 'id_stocks_dividends'})

            df = pd.read_html(str(table), decimal=',', thousands='.')[0]

            return df
        except:
            return None
