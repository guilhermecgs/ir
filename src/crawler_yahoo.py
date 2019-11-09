
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

    dd = parser.xpath(r'/html[@id="atomic"]/body/div[@id="app"]/div/div/div[@id="render-target-default"]/div[@class="Bgc($bg-body) Mih(100%) W(100%) Bgc($layoutBgColor)! finance US"]/div[@id="YDC-Lead"]/div[@id="YDC-Lead-Stack"]/div[@id="YDC-Lead-Stack-Composite"]/div[4]/div[@id="mrt-node-Lead-3-QuoteHeader"]/div[@id="Lead-3-QuoteHeader-Proxy"]/div[@id="quote-header-info"]/div[@class="My(6px) Pos(r) smartphone_Mt(6px)"]/div[@class="D(ib) Va(m) Maw(65%) Ov(h)"]/div[@class="D(ib) Mend(20px)"]/span[@class="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"]')
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
