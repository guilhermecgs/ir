
from collections import OrderedDict
from time import sleep

import requests
import lxml
from lxml import html

def parse(ticker):
    url = "http://finance.yahoo.com/quote/%s?p=%s" % (ticker, ticker)
    response = requests.get(url, verify=False)
    print("Parsing %s" % (url))
    sleep(4)
    parser = html.fromstring(response.text)
    summary_table = parser.xpath('//div[contains(@data-test,"summary-table")]//tr')
    summary_data = OrderedDict()

    try:
        for table_data in summary_table:
            print(lxml.etree.tostring(table_data, pretty_print=True))
            tds = table_data.xpath('.//td//text()')
            table_key = ''.join(tds[0]).strip()
            table_value = ''.join(tds[1]).strip()
            summary_data.update({table_key: table_value})
        summary_data.update({'ticker': ticker, 'url': url})
        return summary_data
    except:
        print("Failed to parse json response")
        return {"error": "Failed to parse json response"}
