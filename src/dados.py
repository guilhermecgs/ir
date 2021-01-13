import datetime
from src.crawler_funds_explorer_bs4 import fii_nome, fii_razao_social, fii_cnpj, fii_ticker_equivalente
from cachier import cachier
import json
import yaml
import bios
import urllib
import re


#
# Para unificar posteriormente os dados de todos ativos em um local generico
#




# No caso das subscrições os códigos vem diferentes e portanto não tem cotação
# Ajusta para o equivalente de forma a obter cotação valida
#   
def ticker_equivalente(ticker):
    return fii_ticker_equivalente(ticker)

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

def ticker_data(ticker, name, default_value=None):
    data = get_data(ticker)
    if data and name in data:
       return data[name]
    return default_value
    
def ticker_codigo_irpf(ticker):
    return None

def get_data(ticker):
    data = __get_data(ticker)
    if data:
        return data
    #TODO isso não está bom precisaria fazer combinação do que tem numero no final com os que não tem número
    # ex BPAC3 BPAC5 BPAC11 todos compartilham alguns dados, mas valores, alvos são diferentes....
    # Para 12,13,14 que tem a ver com as subscrições não parece ter problema....
    # Mas por enquanto para os dados baixados do irpf-cei está ok
    data = __get_data(re.sub("1[1234]$","", ticker))
    return data
    
    
    
def __get_data(ticker):
    data = __get_combined_data()
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

__combined_data = {}
def __get_combined_data():
    global __combined_data
    if len(__combined_data) == 0:
        __combined_data = __get_all_remote_data()
        # Definições locais para ativos, podem ser no formato json como os remotos do irpf-cei ou yaml que são mais faceis de editar
        __combined_data = __load_local('ativos.json', __combined_data)
        __combined_data = __load_local('ativos.yaml', __combined_data)
      
        # TODO: Aqui é possivel colocar dados pessoais, seria interessante buscar no diretorio pessoal
        # ex. valor alvo de um ativo 
        __combined_data = __load_local('ativos-meus-dados.yaml', __combined_data)

        # Gera arquivo para conferencia e acompanhamento com dados combinados    
        with open("ativos-combinado.json", "w") as file:
           json.dump(__combined_data, file, indent=4, sort_keys=True)
        with open("ativos-combinado.yaml", "w") as file:
           yaml.dump(__combined_data, file, sort_keys=True)
    return __combined_data

@cachier(stale_after=datetime.timedelta(days=30))
def __get_all_remote_data():
    data = {}
    data.update(__get_remote_data('ETF'))
    data.update(__get_remote_data('FII'))
    data.update(__get_remote_data('ACAO'))

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
