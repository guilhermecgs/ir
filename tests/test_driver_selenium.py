import unittest

from src.driver_selenium import ChromeDriver


class TestDriverSelenium(unittest.TestCase):

    def test_basic(self):
        driver = None
        driver = ChromeDriver()
        driver.get('https://www.oursky.com/')
        el = driver.find_element_by_class_name('btn-header')
        assert str(el.text).upper() == 'START YOUR PROJECT'
