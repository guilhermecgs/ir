import datetime
from src.crawler_funds_explorer_bs4 import fii_nome, fii_razao_social, fii_cnpj, fii_ticker_equivalente, fii_p_vp, fii_dividend_yield
from cachier import cachier
import pandas as pd
import json
import yaml
import bios
import urllib
import re


#
# Para unificar posteriormente os dados de todos ativos em um local generico
#
# Além disso ao utilizar arquivos com dados agregados reduz o número de chamadas remotas utilizadas para identificar os tipos de ativos
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

def ticker_p_vp(ticker):
    p_vp = ticker_data(ticker, 'p_vp')
    if p_vp:
       return p_vp
       
    if ticker_tipo(ticker) == 'FII':
       return fii_p_vp(ticker)
       
    if ticker_tipo(ticker) == 'ACAO':
       from src.crawler_advfn import advfn_p_vp
           
       return advfn_p_vp(ticker)
       
    return None
    
def ticker_dividend_yield(ticker):
    dividend_yield = ticker_data(ticker, 'dividend_yield')
    if dividend_yield:
       return dividend_yield
       
    if ticker_tipo(ticker) == 'FII':
       return fii_dividend_yield(ticker)
       
    return None
    
def ticker_data(ticker, name, default_value=None):
    data = get_data(ticker)
    if data and name in data:
       return data[name]
    return default_value
    
def ticker_codigo_irpf(ticker):
    return None


def __dict_update_no_replace(old_dict, new_dict):
    if old_dict is None:
       return new_dict
    if new_dict:
        for k in new_dict:
            if not k in old_dict:
                old_dict[k] = new_dict[k]
    return old_dict
    

#
# Busca dados de um ticker especifico mas utilizando a hierarquia dos códigos
#
# Fazendo a combinação com dados menos especificos
# Ex. p/ XXXX14 vai buscar dados de XXXX14, combinar com dados de XXXX11 e depois com dados de XXXX
#
# Dessa forma não é necessário ter dados replicados entre os diversos elementos e o dado mais especifico é prioritario
#    
def get_data(ticker):
    data = __get_data(ticker)
    t1 = fii_ticker_equivalente(ticker)
    if t1 != ticker:
        data = __dict_update_no_replace(data, __get_data(t1))
    t2 = re.sub("[0-9]+$","", t1)
    if t2 != t1:
        data = __dict_update_no_replace(data, __get_data(t2))
    return data
    
    
    
def __get_data(ticker):
    data = __get_combined_data()
    return data[ticker] if ticker in data else None
    

# Faz atualização de dicionario, gerando aviso nas mudanças
# Facilita para identificar erros no cadastro local ou remoto
def __update(dict, key, value, context, message_on_change=True):
    # Ignora mudancas quando forem somente espacos
    if key in dict and ( "".join(str(dict[key]).split()) != "".join(str(value).split()) ) and message_on_change:
        print("Alterando valor da chave " + key + " de " + dict[key] + " para " + value + " em " + context)
    dict[key] = value
        
        
def __load_local(name, data):
    try:
       localData = bios.read(name)
       for k in localData:
          for t in k.strip().split("-"):
             # é possivel definir no arquivo sem dados então verifica aqui se tem dados antes de processar...
             if localData[k]:
                 if t in data:
                    for kl in localData[k]:
                        __update(data[t], kl, localData[k][kl], k)
                 else:
                    data[t] = localData[k]
    except FileNotFoundError:
       pass
    except Exception as ex:
       print("*** Erro carregando dados locais : " + name)
       print(ex)
       raise ex
    return data

reFII = re.compile(".*((FDO|FUNDO).*INV.*IMOB|FII).*")

def __load_instruments(name, data):
    # http://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/consultas/boletim-diario/arquivos-para-download/
    # arquivo com dados diarios da B3 traz algumas informações adicionais em formato csv
    # Não é necessário baixar sempre o arquivo somente quando a lista de ativos mudar
    try:
       instruments = pd.read_csv(name, 
                       header=0,
                       sep=';',
                       decimal=',',
                       encoding='iso-8859-1', 
                       parse_dates=True,
                       comment='#')
       # http://www.b3.com.br/data/files/53/44/8F/3A/DCDFD610BB692DD6AC094EA8/Catalogo_de_Taxonomia_UP2DATA_-_Portugues.pdf
       # http://www.b3.com.br/data/files/88/57/AB/07/D7A6E610B60806E6AC094EA8/Cadastro%20de%20Instrumentos%20_Listados_.pdf
       #
       # TckrSymb - ticker
       # CrpnNm - Nome da Empresa
       # SgmtNm - segmento (1o nivel de classificacao)
       # MktNm  - 2o nivel de classificacao
       # SctyCtgyNm - categoria - SHARES UNIT FUNDS (3o nivel de classificacao)
       # XprtnDt - Vencimento ?
       # TradgStartDt - Data inicial ?
       # TradgEndDt - Data Final 
       # ISIN
       # CtrctMltplr - Multiplicador do contrato (decimal com virgula)
       # AsstQtnQty - Quantidade de negociacao
       # AllcnRndLot - Tamanho de lote para alocação
       # TradgCcy - moeda
       # WdrwlDays - dias uteis de saque até data de vencimento
       # WrkgDays - dias uteis para vencimento do contrato
       # ClnrDays - dias corridos/calendario até vencimento do contrato
       # DaysToSttlm - Dias para liquidacao
       # PrtcnFlg - Protection Flag
       # SpcfctnCd - Especificacao das ações
       # CtdyTrtmntTpNm - Codigo de Tratamento de Custódia
       # MktCptlstn - valor do capital social
       # CorpGovnLvlNm - Nivel de governança
       instruments = instruments.rename(columns={'TckrSymb': 'ticker', 
                             'CrpnNm' : 'nome', 
                             'SgmtNm' : 'segmento',
                             'MktNm'  : 'segmento2',
                             'ISIN'   : 'isin',
                             'SctyCtgyNm' : 'categoria',
                             'AllcnRndLot' : 'lote',
                             'DaysToSttlm' : 'dias_liquidacao',
                             'SpcfctnCd' : 'tipo_acao',
                             'MktCptlstn' : 'capital_social',
                             'CorpGovnLvlNm' : 'nivel_governanca' })
       instruments = instruments[instruments['segmento2'] == 'EQUITY-CASH']
       
       for i,row in instruments.iterrows():
          if not row.ticker in data:
             data[row.ticker] = {}
          # Os nomes do arquivo B3 são melhores que os do irpf-cei então substitui sem mensagem
          __update(data[row.ticker], 'nome', row['nome'], row.ticker, message_on_change=False)
          __update(data[row.ticker], 'isin', row['isin'], row.ticker)
          __update(data[row.ticker], 'capital_social', row['capital_social'], row.ticker)
          __update(data[row.ticker], 'tipo_acao', row['tipo_acao'], row.ticker)
          # Aparentemente mesmo os que são negociados em lote de 100 vem como 1
          __update(data[row.ticker], 'lote', row['lote'], row.ticker)
          cat = str(row['categoria'])
          __update(data[row.ticker], 'categoria', cat, row.ticker)
          __update(data[row.ticker], 'ticker', row.ticker, row.ticker)

          if cat.startswith('ETF'):
             __update(data[row.ticker], 'tipo', 'ETF', row.ticker)
          elif cat.startswith('BDR'):
             __update(data[row.ticker], 'tipo', 'BDR', row.ticker)
          elif row['nome'].startswith('TAXA'):
             __update(data[row.ticker], 'tipo', 'TAXA', row.ticker)
          elif cat == 'SHARES' or cat == 'UNIT':
             __update(data[row.ticker], 'tipo', 'ACAO', row.ticker)
          elif cat == 'FUNDS':
              if reFII.match(row.nome):
                 __update(data[row.ticker], 'tipo', 'FII', row.ticker)
              else:
                 print("TIPO DESCONHECIDO : " + row.ticker + "|" + row.nome + "|" + cat + "|" + row['tipo_acao'])
             
    except Exception as ex:
       print("*** Erro carregando instrumentos B3")
       print(ex)
    return data
    
__combined_data = {}
def __get_combined_data():
    global __combined_data
    if len(__combined_data) == 0:
        __combined_data = __get_all_remote_data()
        
        # Dados locais tem prioridade sobre dados que são baixados automaticamente do irpf-cei
        # Se baixou dados de instrumentos vai carregar por cima dos remotos
        __combined_data = __load_instruments('InstrumentsConsolidatedFile.csv', __combined_data)

        # Definições locais para ativos, podem ser no formato json como os remotos do irpf-cei ou yaml que são mais faceis de editar
        __combined_data = __load_local('ativos.json', __combined_data)
        __combined_data = __load_local('ativos.yaml', __combined_data)
      
        # TODO: Aqui é possivel colocar dados pessoais, seria interessante buscar no diretorio pessoal
        # ex. valor alvo de um ativo 
        __combined_data = __load_local('ativos-meus-dados.yaml', __combined_data)

        # Gera arquivo para conferencia e acompanhamento com dados combinados    
        try:

           with open("ativos-combinado.json", "w") as file:
              json.dump(__combined_data, file, indent=4, sort_keys=True)

           with open("ativos-combinado.yaml", "w") as file:
              yaml.dump(__combined_data, file, sort_keys=True)

        except Exception as ex:
           print("*** Erro salvando lista combinada de ativos")
           print(ex)

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
            for t in i['ticker'].strip().split('-'):
                # Alguns elementos vem com espaços
                t = t.strip()
                i['ticker'] = t
                data.update({ t : i.copy() })
    return data

#with open("corretoras.json", "r") as json_file:
#    result = convert_list_to_dict(json.load(json_file), "CodB3", "Cnpj")
#    print(len(result))
#    print(result)    
