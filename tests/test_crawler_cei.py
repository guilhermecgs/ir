import unittest

from src.selenium import configure_driver
from src.crawler_cei import CrawlerCei
import pandas as pd


class TestCrawlerCei_Selenium(unittest.TestCase):

    def test_basic(self):
        driver = None
        try:
            driver = configure_driver(headless=True)
            driver.get('https://www.oursky.com/')
            el = driver.find_element_by_class_name('btn-header')
            assert str(el.text).upper() == 'START YOUR PROJECT'
        except:
            raise Exception()
        finally:
            driver.quit()

    def test_busca_trades(self):
        directory = '../public/'
        import os
        if not os.path.exists(directory):
            os.makedirs(directory)

        crawler_cei = CrawlerCei(headless=True, directory=directory, debug=True)
        trades = crawler_cei.busca_trades()
        assert type(trades) is pd.DataFrame
        assert len(trades)