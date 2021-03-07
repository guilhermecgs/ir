import sys
from bs4 import BeautifulSoup

import pandas as pd
from selenium import webdriver
import chromedriver_binary  # do not remove

from src.tipo_ticker import TipoTicker
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from cachier import cachier
import datetime

from src.utils import CACHE_DIR

this = sys.modules[__name__]

this.advfn = None


@cachier(stale_after=datetime.timedelta(hours=3), cache_dir=CACHE_DIR)
def __busca_parametros(ticker):
    ticker = ticker.lower()

    try:
        if this.advfn is None:
            this.advfn = CrawlerAdvfn()
        return this.advfn.recupera_informacoes(ticker)

    except Exception:
        return None


def __busca(ticker, parametro):
    dados = __busca_parametros(ticker)
    if (dados is not None) and (parametro in dados):
        return dados[parametro]
    return None


def advfn_preco_atual(ticker):
    return __busca(ticker, 'preco_atual')


def advfn_tipo_ticker(ticker):
    return __busca(ticker, 'tipo_ticker')


class CrawlerAdvfn():

    def __init__(self):
        from src.driver_selenium import ChromeDriver
        self.driver = ChromeDriver()

    def __get_url(self, ticker):
        return 'https://br.advfn.com/bolsa-de-valores/bmf/{ticker}/cotacao'.format(ticker=ticker)

    def recupera_informacoes(self, ticker):
        self.driver.get(self.__get_url(ticker))

        tipo_ticker = self.__recupera_tipo_ticker(ticker)

        preco_atual = self.__recupera_preco_atual()

        return {'tipo_ticker': tipo_ticker, 'preco_atual': preco_atual}

    def __recupera_preco_atual(self):
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, 'quoteElementPiece10')))
            preco_atual = float(self.driver.find_element_by_id('quoteElementPiece10').text
                                .replace('.', '').replace(',', '.'))
            return preco_atual
        except Exception:
            return None

    def __recupera_tipo_ticker(self, ticker):
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, 'quoteElementPiece5')))
            tipo = self.driver.find_element_by_id('quoteElementPiece5').text.lower()
            isin = self.driver.find_element_by_id('quoteElementPiece6').text.lower()

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

            if (tipo == 'recibo de depósito') and ('bdr' in isin):
                return TipoTicker.BDR

        except Exception:
            pass
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