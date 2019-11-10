
def e_tipo_etf(ticker: str):
    etfs = []
    etfs.append('BBSD')
    etfs.append('XBOV')
    etfs.append('BOVB')
    etfs.append('IVVB')
    etfs.append('BOVA')
    etfs.append('BRAX')
    etfs.append('ECOO')
    etfs.append('SMAL')
    etfs.append('BOVV')
    etfs.append('DIVO')
    etfs.append('FIND')
    etfs.append('GOVE')
    etfs.append('MATB')
    etfs.append('ISUS')
    etfs.append('PIBB')
    etfs.append('SPXI')
    return ticker.replace('11', '').upper() in etfs


# def e_tipo_etf(ticker: str):
#     import ssl
#     from urllib.request import Request, urlopen
#     from bs4 import BeautifulSoup
#
#     try:
#         # For ignoring SSL certificate errors
#         ctx = ssl.create_default_context()
#         ctx.check_hostname = False
#         ctx.verify_mode = ssl.CERT_NONE
#
#         ticker_caps = ticker.upper()
#         url = 'https://br.investing.com/etfs/brazil-etfs'
#
#         # Making the website believe that you are accessing it using a Mozilla browser
#         req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
#         webpage = urlopen(req).read()
#
#         soup = BeautifulSoup(webpage, 'html.parser')
#         # html = soup.prettify('utf-8')
#
#         for td in soup.findAll('td', attrs={'title': ticker_caps}):
#             return True
#
#         return False
#     except Exception as ex:
#         return False