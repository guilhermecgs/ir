from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import chromedriver_binary


def busca_trades():

    print(chromedriver_binary.chromedriver_filename)

    """Start web driver"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)

    try:
        driver.get('https://www.oursky.com/')
        el = driver.find_element_by_class_name('btn-header')
        el.click()
    except NoSuchElementException as ex:
        pass

    driver.quit()
