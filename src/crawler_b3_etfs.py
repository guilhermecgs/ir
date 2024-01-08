import sys

import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.driver_selenium import ChromeDriver
from cachier import cachier
import datetime

from src.utils import CACHE_DIR


def __converte_etfs_para_dataframe(driver):
    id_table = 'ctl00_contentPlaceHolderConteudo_etf_pgvETFsRendaVariavel'
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, id_table)))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    div = soup.find('div', {'id': id_table})
    table = div.find(lambda tag: tag.name == 'table')
    df = pd.read_html(str(table), decimal=',', thousands='.')[0]
    return df


def __busca_etfs_na_b3():
    try:
        url = 'http://bvmf.bmfbovespa.com.br/etf/fundo-de-indice.aspx?idioma=pt-br&aba=tabETFsRendaVariavel'
        driver = ChromeDriver()
        driver.get(url)

        etfs = __converte_etfs_para_dataframe(driver)
        return set(etfs['Código'])
    except:
        return set()


@cachier(stale_after=datetime.timedelta(days=15), cache_dir=CACHE_DIR)
def __etfs():
    etfs_hardcoded = set()  # b3 site não tem uma disponibilidade boa
    etfs_hardcoded.add('AGRI')
    etfs_hardcoded.add('BBOV')
    etfs_hardcoded.add('DVER')
    etfs_hardcoded.add('BBOI')
    etfs_hardcoded.add('CORN')
    etfs_hardcoded.add('BBSD')
    etfs_hardcoded.add('BMMT')
    etfs_hardcoded.add('BREW')
    etfs_hardcoded.add('BDEF')
    etfs_hardcoded.add('IBOB')
    etfs_hardcoded.add('ESGB')
    etfs_hardcoded.add('SPXB')
    etfs_hardcoded.add('GENB')
    etfs_hardcoded.add('SMAB')
    etfs_hardcoded.add('CMDB')
    etfs_hardcoded.add('SPYI')
    etfs_hardcoded.add('XBOV')
    etfs_hardcoded.add('CRPT')
    etfs_hardcoded.add('BOVB')
    etfs_hardcoded.add('TRIG')
    etfs_hardcoded.add('META')
    etfs_hardcoded.add('DEFI')
    etfs_hardcoded.add('BITH')
    etfs_hardcoded.add('HASH')
    etfs_hardcoded.add('ETHE')
    etfs_hardcoded.add('WEB3')
    etfs_hardcoded.add('TECB')
    etfs_hardcoded.add('GURU')
    etfs_hardcoded.add('PEVC')
    etfs_hardcoded.add('5GTK')
    etfs_hardcoded.add('JOGO')
    etfs_hardcoded.add('FOOD')
    etfs_hardcoded.add('ALUG')
    etfs_hardcoded.add('USTK')
    etfs_hardcoded.add('SVAL')
    etfs_hardcoded.add('WRLD')
    etfs_hardcoded.add('BDOM')
    etfs_hardcoded.add('BXPO')
    etfs_hardcoded.add('SCVB')
    etfs_hardcoded.add('BTEK')
    etfs_hardcoded.add('BLOK')
    etfs_hardcoded.add('NFTS')
    etfs_hardcoded.add('SMAL')
    etfs_hardcoded.add('BOVA')
    etfs_hardcoded.add('BRAX')
    etfs_hardcoded.add('ECOO')
    etfs_hardcoded.add('IVVB')
    etfs_hardcoded.add('BITI')
    etfs_hardcoded.add('BOVV')
    etfs_hardcoded.add('DIVO')
    etfs_hardcoded.add('FIND')
    etfs_hardcoded.add('GOVE')
    etfs_hardcoded.add('MATB')
    etfs_hardcoded.add('ISUS')
    etfs_hardcoded.add('HTEK')
    etfs_hardcoded.add('DNAI')
    etfs_hardcoded.add('MILL')
    etfs_hardcoded.add('TECK')
    etfs_hardcoded.add('PIBB')
    etfs_hardcoded.add('REVE')
    etfs_hardcoded.add('YDRO')
    etfs_hardcoded.add('SHOT')
    etfs_hardcoded.add('SPXI')
    etfs_hardcoded.add('SMAC')
    etfs_hardcoded.add('BCIC')
    etfs_hardcoded.add('NSDV')
    etfs_hardcoded.add('NDIV')
    etfs_hardcoded.add('QDFI')
    etfs_hardcoded.add('QBTC')
    etfs_hardcoded.add('QETH')
    etfs_hardcoded.add('ELAS')
    etfs_hardcoded.add('BOVS')
    etfs_hardcoded.add('USAL')
    etfs_hardcoded.add('URET')
    etfs_hardcoded.add('BOVX')
    etfs_hardcoded.add('XFIX')
    etfs_hardcoded.add('GOLD')
    etfs_hardcoded.add('ACWI')
    etfs_hardcoded.add('XINA')
    etfs_hardcoded.add('ESGD')
    etfs_hardcoded.add('ESGE')
    etfs_hardcoded.add('EURP')
    etfs_hardcoded.add('UTEC')
    etfs_hardcoded.add('ESGU')
    etfs_hardcoded.add('NASD')

    return __busca_etfs_na_b3().union(etfs_hardcoded)


def e_tipo_etf(ticker: str):
    return ticker.replace('11', '').upper() in __etfs()
