from selenium import webdriver
import chromedriver_binary  # do not remove


class ChromeDriver(object):

    instance = None

    def __new__(cls):

        if cls.instance is None:
            i = object.__new__(cls)
            cls.instance = i
            cls.driver = ChromeDriver.__configure_driver(headless=True)
            i = cls.instance

        return cls.driver

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







