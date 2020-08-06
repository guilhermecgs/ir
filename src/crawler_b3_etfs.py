import sys

import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.driver_selenium import ChromeDriver

this = sys.modules[__name__]
this.etfs = None


def __converte_etfs_para_dataframe(driver):
    id_table = 'ctl00_contentPlaceHolderConteudo_etf_pgvETFsRendaVariavel'
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, id_table)))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    div = soup.find('div', {'id': id_table})
    table = div.find(lambda tag: tag.name == 'table')
    df = pd.read_html(str(table), decimal=',', thousands='.')[0]
    return df


def __busca_etfs_na_b3():
    url = 'http://bvmf.bmfbovespa.com.br/etf/fundo-de-indice.aspx?idioma=pt-br&aba=tabETFsRendaVariavel'
    driver = ChromeDriver()
    driver.get(url)

    etfs = __converte_etfs_para_dataframe(driver)
    return etfs['Código'].tolist()


def __etfs():
    if this.etfs is None:
        this.etfs = __busca_etfs_na_b3()
    return this.etfs


def e_tipo_etf(ticker: str):
    return ticker.replace('11', '').upper() in __etfs()
