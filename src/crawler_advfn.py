import sys
from bs4 import BeautifulSoup

import pandas as pd
from selenium import webdriver
import chromedriver_binary  # do not remove

from src.tipo_ticker import TipoTicker
from cachier import cachier
import datetime

from src.utils import CACHE_DIR


this = sys.modules[__name__]

this.advfn = None


@cachier(stale_after=datetime.timedelta(hours=3), cache_dir=CACHE_DIR)
def busca_parametros(ticker):
    ticker = ticker.lower()

    try:
        if this.advfn is None:
            this.advfn = CrawlerAdvfn()
        return this.advfn.recupera_informacoes(ticker)

    except Exception:
        return None


def __busca(ticker, parametro):
    dados = busca_parametros(ticker)
    if (dados is not None) and (parametro in dados):
        return dados[parametro]
    return None


def advfn_preco_atual(ticker):
    return __busca(ticker, 'preco_atual')


def advfn_tipo_ticker(ticker):
    return __busca(ticker, 'tipo_ticker')


class CrawlerAdvfn():

    ULTIMO_PRECO = 'Último Preço'
    TIPO_ATIVO = 'Tipo de Ativo'

    def __init__(self):
        from src.driver_selenium import ChromeDriver
        self.driver = ChromeDriver()
        self.infos = {}

    def __get_url(self, ticker):
        return 'https://br.advfn.com/bolsa-de-valores/bmf/{ticker}/cotacao'.format(ticker=ticker)

    def recupera_informacoes(self, ticker):
        self.driver.get(self.__get_url(ticker))
        self.infos = self.__parse_de_informacoes_das_tabelas_html()

        tipo_ticker = self.__recupera_tipo_ticker()

        preco_atual = self.__recupera_preco_atual()

        return {'tipo_ticker': tipo_ticker, 'preco_atual': preco_atual}

    def __recupera_preco_atual(self):
        try:
            return self.infos[self.ULTIMO_PRECO]
        except Exception:
            return None

    def __recupera_tipo_ticker(self):
        try:
            if self.__ticker_eh_futuro():
                return TipoTicker.FUTURO

            if self.__ticker_eh_acao():
                return TipoTicker.ACAO_OU_ETF

            if self.__ticker_eh_opcao():
                return TipoTicker.OPCAO

            if self.__ticker_eh_fii():
                return TipoTicker.FII

            if self.__ticker_eh_etf():
                return TipoTicker.ACAO_OU_ETF

            if self.__ticker_eh_bdr():
                return TipoTicker.BDR
        except Exception:
            pass
        return None

    def __ticker_eh_futuro(self):
        return 'Nome do Futuro' in self.infos

    def __ticker_eh_opcao(self):
        return self.TIPO_ATIVO in self.infos and self.infos[self.TIPO_ATIVO].lower() in ['opção']

    def __ticker_eh_acao(self):
        return self.TIPO_ATIVO in self.infos and self.infos[self.TIPO_ATIVO].lower() in ['ordinária', 'preferencial', 'unit']

    def __ticker_eh_bdr(self):
        return self.TIPO_ATIVO in self.infos and self.infos[self.TIPO_ATIVO].lower() in ['recibo de depósito']

    def __ticker_eh_etf(self):
        try:
            nome = self.driver.find_elements_by_class_name("page-name-h1")[0].text.lower()
            if self.TIPO_ATIVO in self.infos and \
                    self.infos[self.TIPO_ATIVO].lower() in ['fundo'] and 'ishares' in nome:
                return True

            return False
        except Exception as ex:
            return False

    def __ticker_eh_fii(self):
        try:
            dividendos = self.__converte_tabela_dividendos_para_df()

            if ('imobiliario' in self.infos['Nome da Ação'].lower()
                or 'fii' in self.infos['Nome da Ação'].lower() 
                or 'fundos imobiliários' in self.infos['Setor da Empresa'].lower()) \
                    and self.infos[self.TIPO_ATIVO].lower() in ['fundo'] and len(dividendos):
                return True
            else:
                return False
        except:
            return False

    def __parse_de_informacoes_das_tabelas_html(self):
        infos = {}

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        for div in soup.findAll('div', {'class': 'TableElement'}):
            try:
                df = pd.read_html(str(div), decimal=',', thousands='.')[0]
                infos.update(df.to_dict('records')[0])
            except:
                pass

        return infos

    def __converte_tabela_dividendos_para_df(self):
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            table = soup.find('table', {'id': 'id_stocks_dividends'})

            df = pd.read_html(str(table), decimal=',', thousands='.')[0]

            return df
        except:
            return None
