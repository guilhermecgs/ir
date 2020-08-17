from selenium import webdriver
import chromedriver_binary  # do not remove


class ChromeDriver(object):

    def __new__(cls):
        return ChromeDriver.__configure_driver(headless=True)

    @staticmethod
    def __configure_driver(headless):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(20)
        return driver







