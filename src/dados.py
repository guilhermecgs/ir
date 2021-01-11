import datetime
from src.crawler_funds_explorer_bs4 import fii_nome, fii_razao_social, fii_cnpj
from cachier import cachier
import json
import bios
import urllib
import re

#
# TODO: tratar para os outros tipos de ativos
#
def ticker_tipo(ticker):
    return ticker_data(ticker,'tipo')
    
def ticker_nome(ticker):
    nome = ticker_data(ticker, 'nome')
    if nome:
       return nome
    return fii_nome(ticker)
    
def ticker_cnpj(ticker):
    cnpj = ticker_data(ticker,'cnpj')
    if cnpj:
       return cnpj
    return fii_cnpj(ticker)

def ticker_data(ticker, name):
    data = get_data(ticker)
    if data and name in data:
       return data[name]
    return None
    
def ticker_codigo_irpf(ticker):
    return None

def get_data(ticker):
    data = __get_data(ticker)
    if data:
        return data
    data = __get_data(re.sub("1[1234]$","", ticker))
    return data
    
    
    
def __get_data(ticker):
    data = __get_all_remote_data()
    return data[ticker] if ticker in data else None
    
def __load_local(name, data):
    try:
       localData = bios.read(name)
       for k in localData:
          for t in k.split("-"):
             if t in data:
                for kl in localData[k]:
                    data[t][kl] = localData[k][kl]
             else:
                data[t] = localData[k]
    except FileNotFoundError:
       pass
    except Exception as ex:
       print(ex)
       raise ex
    return data

@cachier(stale_after=datetime.timedelta(days=30))
def __get_all_remote_data():
    data = {}
    data.update(__get_remote_data('ETF'))
    data.update(__get_remote_data('FII'))
    data.update(__get_remote_data('ACAO'))

    data = __load_local('ativos.json', data)
    data = __load_local('ativos.yaml', data)
    
    with open("ativos-combinado.json", "w") as file:
       json.dump(data, file, indent=4, sort_keys=True)
    return data
    

__defs = { 'ETF' : { 'url' : 'https://raw.githubusercontent.com/staticdev/irpf-cei/master/resources/etfs.json', 
                     'mapa' : { 'Codigo' : 'ticker', 'Cnpj' : 'cnpj', 'Fundo' : 'fundo', 'RazaoSocial' : 'nome' } 
                     },
           'FII' : { 'url' : 'https://raw.githubusercontent.com/staticdev/irpf-cei/master/resources/fiis.json', 
                     'mapa' : { 'codigo' : 'ticker' }
                     },
            'ACAO' : { 'url' : 'https://raw.githubusercontent.com/staticdev/irpf-cei/master/resources/empresas.json', 
                     'mapa' : { 'codigo' : 'ticker', 'empresa' : 'nome' }
                     }                       
        }
        
        
@cachier(stale_after=datetime.timedelta(days=30))
def __get_remote_data(tipo):
    data = {}
    with urllib.request.urlopen(__defs[tipo]['url']) as connection:
        arr = json.loads(connection.read().decode())
        mapa = __defs[tipo]['mapa']
        for i in arr:
            i['tipo'] = tipo
            for k in mapa:
                if i[k]:
                    if len(mapa[k]):
                        i[mapa[k]] = i[k]
                    i.pop(k)
            for t in i['ticker'].split('-'):
                i['ticker'] = t
                data.update({ t : i.copy() })
    return data

#with open("corretoras.json", "r") as json_file:
#    result = convert_list_to_dict(json.load(json_file), "CodB3", "Cnpj")
#    print(len(result))
#    print(result)    
