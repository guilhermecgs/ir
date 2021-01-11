import argparse
import os
import sys

import pandas as pd

from datetime import datetime,date
from dateutil.relativedelta import relativedelta
from tabulate import tabulate

from src.calculo_ir import CalculoIr
from src.dropbox_files import upload_dropbox_file, OPERATIONS_FILEPATH
from src.envia_relatorio_por_email import envia_relatorio_html_por_email
from src.relatorio import relatorio_txt, relatorio_html, assunto
from src.planilhas import salva_planilha_irpf
from src.stuff import get_operations, \
    merge_operacoes, \
    merge_outros, \
    df_to_csv

WORK_DIR=''

# Vai processar dados somente até essa data
data_referencia = date.today()
hoje = date.today()

def main(raw_args):
    global WORK_DIR
    global OPERATIONS_FILEPATH
    global data_referencia
    parser = argparse.ArgumentParser()
    parser.add_argument('--do', required=False)
    parser.add_argument('--data', type=lambda s: datetime.strptime(s, '%d/%m/%Y').date())
    parser.add_argument('--html', required=False)
    args = parser.parse_args(raw_args)
    if os.getenv('WORK_DIR'):
       WORK_DIR=os.getenv('WORK_DIR')
       try:
          os.makedirs(WORK_DIR)
       except:
          pass
       OPERATIONS_FILEPATH = WORK_DIR + OPERATIONS_FILEPATH
       print(WORK_DIR)
       print(OPERATIONS_FILEPATH)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)

    if args.data:
        data_referencia = args.data
        
    if args.do == 'busca_trades_e_faz_merge_operacoes':
        do_busca_trades_e_faz_merge_operacoes()
        return

    if args.do == 'busca_carteira':
        do_busca_carteira()
        return

    if args.do == 'salva_carteira':
        do_salva_carteira(args.html)
        return

    if args.do == 'check_environment_variables':
        do_check_environment_variables()
        return

    if args.do == 'calculo_ir':
        do_calculo_ir()
        return

    do_busca_trades_e_faz_merge_operacoes()
    do_calculo_ir()


def do_busca_trades_e_faz_merge_operacoes():
    from src.crawler_cei import CrawlerCei
    crawler_cei = CrawlerCei(headless=True)
    df_cei = crawler_cei.busca_trades()

    from src.dropbox_files import download_dropbox_file
    download_dropbox_file(OPERATIONS_FILEPATH)

    df = get_operations(filepath=OPERATIONS_FILEPATH)
    df = merge_operacoes(df, df_cei)
    df_to_csv(df, OPERATIONS_FILEPATH)

    upload_dropbox_file(OPERATIONS_FILEPATH, None)

def do_busca_carteira():
    from src.crawler_cei import CrawlerCei
    crawler_cei = CrawlerCei(headless=True)
    df_carteira = crawler_cei.busca_carteira(data=data_referencia)

    df_to_csv(df_carteira, WORK_DIR + nome_com_referencia('carteira_cei.txt'), colunas=df_carteira.columns, header=True)

def do_salva_carteira(filepath):
    from src.crawler_cei import CrawlerCei
    crawler_cei = CrawlerCei(headless=True)
    with open(filepath, 'r') as file:
       df_carteira = crawler_cei.converte_html_carteira(file.read())

    df_to_csv(df_carteira, WORK_DIR + nome_com_referencia('carteira_cei.txt'), colunas=df_carteira.columns, header=True)



def do_check_environment_variables():
    from tests.test_environment_variables import TestEnvironmentVariables
    TestEnvironmentVariables().test_environment_variables()


def save_to_daily_file(ext, content):
    with open(WORK_DIR + data_referencia.strftime('%Y-%m-%d') + "." + ext, "w") as text_file:
        print(content, file=text_file)

def save_to_file(name, content):
    with open(WORK_DIR + name, "w") as text_file:
        print(content, file=text_file)
  
# Para casos onde foi executado com data diferente da atual é interessante salvar arquivo especifico e não em cima do arquivo generico      
# Isso facilita a analise em datas especificas
def nome_com_referencia(nome):
   return('' if data_referencia == hoje else data_referencia.strftime('%Y-%m-%d') + "-") + nome 


#
# No final do ano a liquidação acaba acontecendo no ano seguinte e a mudança da carteira
# então o mais simples é alterar a data da operação jogando para o ano seguinte
# O ideal é ter uma tabela indicando quais ajustes devem ser feitos
#
def ajusta_data(data):
    if (data.month == 12) and (data.day >= 29):
       return date(data.year+1, 1, 1)
    return data
    
def ajusta_datas(df, coluna):
    #TODO fazer ajuste nas datas de operações de final de ano que foram finalizadas no ano seguinte
    df[coluna] = df.apply(lambda row: ajusta_data(row[coluna]), axis=1)
    return df


def carrega_notas_corretagem(pref):
    colunasNotasCorretagem = [ 'data','corretora','valor' ]
    try:
        # DATA(DD/MM/YYYY) CORRETORA VALOR
        notas = pd.read_csv(WORK_DIR + pref + 'notas-corretagem.txt', 
                         sep='\t',
                         header=None,
                         parse_dates=[0],
                         dayfirst=True,
                         comment='#')
        notas = notas[[0,1,2]]
        notas.columns = colunasNotasCorretagem
    except FileNotFoundError:
        notas = pd.DataFrame(columns=colunasNotasCorretagem)
    except Exception as e:
        print(e)
        notas = pd.DataFrame(columns=colunasNotasCorretagem)
    # Como é carregado como datetime, converte para permitir a comparação correta
    notas['verificado'] = notas.apply(lambda row: False, axis=1)
    if len(notas) > 0:
        notas = ajusta_datas(notas, 'data')
        notas['data'] = notas.apply(lambda row: row['data'].date(), axis=1)
        notas.drop(notas[notas['data'] > data_referencia].index, inplace=True)
    return notas
        
#
# Gera resumo de operações diarias
# Caso tenha arquivo com valores das notas de corretagem compara para detectar possiveis erros nos dados
#
def do_diario(df, first_year, last_year):
    diario = df.copy()
    diario['valor_operacao'] = diario.apply(lambda row: row.qtd * row.preco, axis=1)
    diario['compra'] = diario.apply(lambda row: row.ticker if row.qtd > 0 else '', axis=1)
    diario['venda'] = diario.apply(lambda row: row.ticker if row.qtd < 0 else '', axis=1)
    diario = diario.groupby('data', as_index=False, sort=True).agg({ 'valor_operacao' : 'sum', 'taxas' : 'sum', 'compra' : 'unique', 'venda' : 'unique' })
    diario['total'] = diario.apply(lambda row: row.valor_operacao + row.taxas, axis=1)
    diario['notas_corretagem'] = diario.apply(lambda row: 0, axis=1)

    txtNotas = ''
    
    try:
        notas = carrega_notas_corretagem('')
        for year in range(first_year,last_year):
           n = carrega_notas_corretagem('/' + str(year) + '/')
           notas = notas.append(n, ignore_index=True)
        
        for i, row in diario.iterrows():
            for iN, rowN in notas.iterrows():
               if row['data'] == rowN['data']:
                  diario.loc[i,'notas_corretagem'] = row['notas_corretagem'] + rowN['valor']
                  notas.loc[iN,'verificado'] = True
        notas = notas[notas.verificado == False]
        if notas.size > 0:
           notas = notas[['data','corretora','valor']]
           txtNotas = "*** NOTAS SEM OPERACOES NO DIA : \n" + tabulate(notas, headers=['Data', 'Corretora', 'Valor'], showindex=False, tablefmt='psql')
           print(txtNotas)
                  
    except Exception as e:
        print("** ERRO CARREGANDO NOTAS DE CORRETAGEM")
        print(e)

    diario['diferenca_notas_corretagem'] = diario.apply(lambda row: round(row.total - row.notas_corretagem,2), axis=1)

    txt = tabulate(diario, showindex=False, headers=['Data','Operações','Custos', 'Compras', 'Vendas','Total', 'Notas', 'Diferença Notas'], tablefmt='psql')
    save_to_file(nome_com_referencia('diario.txt'), txt + '\n' + txtNotas)

def do_calculo_ir():
    from src.dropbox_files import download_dropbox_file
    download_dropbox_file(OPERATIONS_FILEPATH)
    df = get_operations(filepath=OPERATIONS_FILEPATH)

    first_year = df['data'].min().year
    last_year = df['data'].max().year
    # Permite separar as outras operações de forma organizada
    for f in ['outras_operacoes.txt', 'custos.txt', 'ofertas_publicas.txt', 'subscricoes.txt']:
       for year in range(first_year, last_year):
          outros = get_operations(WORK_DIR + str(year) + '/' + f, operations=df)
          df = merge_outros(df, outros)
       outros = get_operations(WORK_DIR + f, operations=df)
       df = merge_outros(df, outros)

    df.reset_index(drop=True, inplace=True)
    df = ajusta_datas(df, 'data')
    df.drop(df[df['data'] > data_referencia].index, inplace=True)

    if len(df) == 0:
        raise Exception("Não existem dados para processar até a data : " + str(data_referencia))
        
    df_to_csv(df, WORK_DIR + nome_com_referencia('combinado.txt'))
    do_diario(df.copy(), first_year, last_year)
    
    from src.stuff import calcula_custodia

    # Custódia e IR são gerados somente uma vez e passados para os relatórios
    custodia = calcula_custodia(df)
    calculo_ir = CalculoIr(df=df)
    calculo_ir.calcula()

    declaracao_anual = data_referencia.strftime('%m%d') == '1231'
    if declaracao_anual:
       adicionais = {}
       # final do ano gerar relatorio para facilitar IRPF Anual
       print("*** GERAR RELATORIO PARA IRPF")
       try:
          carteira_cei = pd.read_csv(WORK_DIR + nome_com_referencia('carteira_cei.txt'),
                                    sep='\t',
                                    header=0)
          carteira_cei = carteira_cei.groupby('ticker', as_index=False, sort=True).agg({ 'qtd' : 'sum' })
          for a,ra in custodia.iterrows():
             carteira_cei['qtd'] = carteira_cei.apply(lambda row: row.qtd - ra.qtd if row.ticker == ra.ticker else row.qtd, axis=1)
             # Verificando se tem itens na custodia que não estão na carteira cei
             filtro = carteira_cei[carteira_cei['ticker'] == ra.ticker]
             if len(filtro) == 0:
                print("*** " + ra.ticker + " não está na carteira CEI")
                carteira_cei = carteira_cei.append({ 'ticker' : ra.ticker, 'qtd' : ra.qtd*-1}, ignore_index=True)

          carteira_cei = carteira_cei[carteira_cei['qtd'] != 0]
          if len(carteira_cei) > 0:
              print("*** ERRO NA COMPARACAO COM CARTEIRA CEI : ")
              print(carteira_cei)
              adicionais['diferenca_carteira_cei'] = carteira_cei
              
       except FileNotFoundError:
          pass
       except Exception as e:
          print("Erro lendo carteira_cei.txt ")
          print(e)
                     
       salva_planilha_irpf(WORK_DIR + nome_com_referencia('custodia.xlsx'), custodia, adicionais)
       
    txt = relatorio_txt(custodia.copy(), calculo_ir, data_referencia, declaracao_anual)
    save_to_daily_file("txt", txt);
    print(txt)

    html = relatorio_html(custodia.copy(), calculo_ir, data_referencia, declaracao_anual)
    save_to_daily_file("html", html)
    envia_relatorio_html_por_email(assunto(calculo_ir), html)


if __name__ == "__main__":
    main(sys.argv[1:])
    
    