import unittest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import chromedriver_binary


class TestCrawlerCei_Selenium(unittest.TestCase):
    """Include test cases on a given url"""

    def setUp(self):

        print(chromedriver_binary.chromedriver_filename)
        """Start web driver"""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)

    def tearDown(self):
        """Stop web driver"""
        self.driver.quit()

    def test_case_1(self):
        """Find and click top-right button"""
        try:
            self.driver.get('https://www.oursky.com/')
            el = self.driver.find_element_by_class_name('btn-header')
            print('TEXTO DO BOTAO ÉDDDDDDD')
            print(el.text)
            el.click()
        except NoSuchElementException as ex:
            self.fail(ex.msg)


