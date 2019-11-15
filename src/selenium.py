import chromedriver_binary  # do not remove
from selenium import webdriver


def configure_driver(headless=False):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    return driver
