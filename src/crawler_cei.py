import os
import time
import pandas as pd
from bs4 import BeautifulSoup
import sys

from selenium import webdriver
import chromedriver_binary  # do not remove
from selenium.common.exceptions import NoSuchElementException
from cachier import cachier
import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.driver_selenium import ChromeDriver
from src.utils import CACHE_DIR


class AnyEc:
    """ Use with WebDriverWait to combine expected_conditions
        in an OR.
    """

    def __init__(self, *args):
        self.ecs = args

    def __call__(self, driver):
        for fn in self.ecs:
            try:
                if fn(driver): return True
            except:
                pass

this = sys.modules[__name__]

this.crawler_cei = None


@cachier(stale_after=datetime.timedelta(days=1), cache_dir=CACHE_DIR)
def busca_trades(cpf, senha_cei):
    try:
        if this.crawler_cei is None:
            this.crawler_cei = CrawlerCei()
        return this.crawler_cei.busca_trades(cpf, senha_cei)
    except Exception as ex:
        return None


class CrawlerCei():

    def __init__(self, directory=None, debug=False):
        self.BASE_URL = 'https://ceiapp.b3.com.br/CEI_Responsivo/'
        self.driver = ChromeDriver()
        self.directory = directory
        self.debug = debug
        self.__colunas_df_cei = ['Data do Negócio', 'Compra/Venda', 'Mercado', 'Prazo/Vencimento', 'Código Negociação',
               'Especificação do Ativo', 'Quantidade', 'Preço (R$)', 'Valor Total(R$)', 'Fator de Cotação']
        self.id_tabela_negociacao_ativos = 'ctl00_ContentPlaceHolder1_rptAgenteBolsa_ctl00_rptContaBolsa_ctl00_pnAtivosNegociados'
        self.id_mensagem_de_aviso = 'CEIMessageDIV'
        self.id_selecao_corretoras = 'ctl00_ContentPlaceHolder1_ddlAgentes'
        self.id_btn_consultar = 'ctl00_ContentPlaceHolder1_btnConsultar'

    def busca_trades(self, cpf, senha_cei):
        try:
            self.driver.get(self.BASE_URL)
            self.__login(cpf, senha_cei)
            df = self.__abre_consulta_trades()
            return self.__converte_dataframe_para_formato_padrao(df)
        finally:
            self.driver.quit()

    def __login(self, cpf, senha_cei):
        if self.debug: self.driver.save_screenshot(self.directory + r'01.png')
        txt_login = self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_txtLogin')
        txt_login.clear()
        txt_login.send_keys(cpf)

        time.sleep(3.0)
        txt_senha = self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_txtSenha')
        txt_senha.clear()
        txt_senha.send_keys(senha_cei)
        time.sleep(3.0)

        if self.debug: self.driver.save_screenshot(self.directory + r'02.png')

        btn_logar = self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_btnLogar')
        btn_logar.click()

        try:
            WebDriverWait(self.driver, 60).until(EC.visibility_of_element_located((By.ID, 'objGrafPosiInv')))
        except Exception:
            raise Exception('Nao foi possivel logar no CEI. Possivelmente usuario/senha errada ou indisponibilidade do site')

        if self.debug: self.driver.save_screenshot(self.directory + r'03.png')

    def __abre_consulta_trades(self):

        def consultar_click(driver):
            btn_consultar = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, self.id_btn_consultar)))
            btn_consultar.click();

        def exists_and_not_disabled(id):
            def until_fn(driver):
                try:
                    driver.find_element_by_id(id)
                except NoSuchElementException:
                    return False
                return driver.find_element_by_id(id).get_attribute("disabled") is None

            return until_fn

        dfs_to_concat = []

        self.driver.get(self.BASE_URL + 'negociacao-de-ativos.aspx')
        if self.debug: self.driver.save_screenshot(self.directory + r'04.png')

        from selenium.webdriver.support.select import Select
        ddlAgentes = Select(self.driver.find_element_by_id(self.id_selecao_corretoras))

        def __busca_trades_de_uma_corretora(i):
            if self.debug: self.driver.save_screenshot(self.directory + r'04_01.png')
            ddlAgentes = Select(self.driver.find_element_by_id(self.id_selecao_corretoras))
            ddlAgentes.select_by_index(i)
            time.sleep(5)
            if self.debug: self.driver.save_screenshot(self.directory + r'04_02.png')
            WebDriverWait(self.driver, 15).until(exists_and_not_disabled(self.id_btn_consultar))
            consultar_click(self.driver)

            if self.debug: self.driver.save_screenshot(self.directory + r'05.png')

            try:
                WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
                    (By.ID, self.id_mensagem_de_aviso)))
            except:
                pass

            if self.debug: self.driver.save_screenshot(self.directory + r'06.png')

            # checa se existem trades para essa corretora
            aviso = self.driver.find_element_by_id(self.id_mensagem_de_aviso)
            if aviso.text == 'Não foram encontrados resultados para esta pesquisa.\n×':
                consultar_click(self.driver)
                WebDriverWait(self.driver, 60).until(exists_and_not_disabled(self.id_selecao_corretoras))
            else:
                if not exists_and_not_disabled(self.id_tabela_negociacao_ativos)(self.driver):
                    consultar_click(self.driver)

                WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(
                    (By.ID, self.id_tabela_negociacao_ativos)))

                dfs_to_concat.append(self.__converte_trades_para_dataframe())
                consultar_click(self.driver)
                try:
                    WebDriverWait(self.driver, 20).until(exists_and_not_disabled(self.id_selecao_corretoras))
                except:
                    self.driver.get(self.BASE_URL + 'negociacao-de-ativos.aspx')

        if len(ddlAgentes.options) == 1:
            __busca_trades_de_uma_corretora(0)
        else:
            for i in range(1, len(ddlAgentes.options)):
                __busca_trades_de_uma_corretora(i)

        if len(dfs_to_concat):
            return pd.concat(dfs_to_concat)
        else:
            return pd.DataFrame(columns=self.__colunas_df_cei)

    def __converte_trades_para_dataframe(self):

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        top_div = soup.find('div', {'id': self.id_tabela_negociacao_ativos})

        table = top_div.find(lambda tag: tag.name == 'table')

        df = pd.read_html(str(table), decimal=',', thousands='.')[0]

        df = df.dropna(subset=['Mercado'])
        return df

    def __converte_dataframe_para_formato_padrao(self, df):
        df = df.rename(columns={'Código Negociação': 'ticker',
                                'Compra/Venda': 'operacao',
                                'Quantidade': 'qtd',
                                'Data do Negócio': 'data',
                                'Preço (R$)': 'preco',
                                'Valor Total(R$)': 'valor'})

        from src.stuff import calculate_add

        def formata_compra_venda(operacao):
            if operacao == 'V':
                return 'Venda'
            else:
                return 'Compra'

        def remove_fracionado_ticker(ticker):
            return ticker[:-1] if ticker.endswith('F') else ticker

        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        df['data'] = df['data'].dt.date
        df['ticker'] = df.apply(lambda row: remove_fracionado_ticker(row.ticker), axis=1)
        df['operacao'] = df.apply(lambda row: formata_compra_venda(row.operacao), axis=1)
        df['qtd_ajustada'] = df.apply(lambda row: calculate_add(row), axis=1)

        df['taxas'] = 0.0
        df['aquisicao_via'] = 'HomeBroker'

        df.drop(columns=['Mercado', 
                         'Prazo/Vencimento', 
                         'Especificação do Ativo',
                         'Fator de Cotação'], inplace=True)
        return df