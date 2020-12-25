import unittest

from src.driver_selenium import ChromeDriver


class TestDriverSelenium(unittest.TestCase):

    def test_basic(self):
        driver = ChromeDriver()
        driver.get('https://palafiita.com/ofertas-publicas/')
        el = driver.find_element_by_class_name('site-description')
        assert str(el.text) == 'Investimentos em Fundos Imobiliários'
