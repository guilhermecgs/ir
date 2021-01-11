import sys

import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.driver_selenium import ChromeDriver
from cachier import cachier
import datetime

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


@cachier(stale_after=datetime.timedelta(days=7))
def __busca_etfs_na_b3_cache():
    url = 'http://bvmf.bmfbovespa.com.br/etf/fundo-de-indice.aspx?idioma=pt-br&aba=tabETFsRendaVariavel'
    driver = ChromeDriver()
    driver.get(url)

    return __converte_etfs_para_dataframe(driver)

def __busca_etfs_na_b3():
    try:
        etfs = __busca_etfs_na_b3_cache()
        return set(etfs['Código'])
    except:
        return set()


def __etfs():
    if this.etfs is None:
        this.etfs = __busca_etfs_na_b3()

        etfs_hardcoded = set()  # b3 site não tem uma disponibilidade boa
        etfs_hardcoded.add('BBSD')
        etfs_hardcoded.add('XBOV')
        etfs_hardcoded.add('BOVB')
        etfs_hardcoded.add('IVVB')
        etfs_hardcoded.add('BOVA')
        etfs_hardcoded.add('BRAX')
        etfs_hardcoded.add('ECOO')
        etfs_hardcoded.add('SMAL')
        etfs_hardcoded.add('BOVV')
        etfs_hardcoded.add('DIVO')
        etfs_hardcoded.add('FIND')
        etfs_hardcoded.add('GOVE')
        etfs_hardcoded.add('MATB')
        etfs_hardcoded.add('ISUS')
        etfs_hardcoded.add('PIBB')
        etfs_hardcoded.add('SMAC')
        etfs_hardcoded.add('SPXI')

        this.etfs = this.etfs.union(etfs_hardcoded)

    return this.etfs

@cachier(stale_after=datetime.timedelta(days=1))
def e_tipo_etf(ticker: str):
    return ticker.replace('11', '').upper() in __etfs()
