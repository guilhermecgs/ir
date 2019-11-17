import datetime
import pandas as pd

from dateutil.relativedelta import relativedelta

from src.dropbox_files import OPERATIONS_FILEPATH
from src.crawler_yahoo_bs4 import busca_preco_atual


def todas_as_colunas():
    return colunas_obrigatorias().extend(['valor', 'qtd_ajustada'])


def colunas_obrigatorias():
    return ['ticker', 'operacao', 'qtd', 'data', 'preco', 'taxas', 'id_carteira', 'aquisicao_via']


def calcula_valor(qtd, preco):
    return abs(qtd) * preco


def calculate_add(row):
    if row['operacao'] == 'Compra':
        return row['qtd']
    else:
        return row['qtd'] * -1


def get_operations_dataframe(filepath=None):
    if not filepath:
        filepath = OPERATIONS_FILEPATH

    df = pd.read_csv(filepath, sep='\t',
                     header=None,
                     parse_dates=[3],
                     dayfirst=True)

    df.columns = ['ticker', 'operacao', 'qtd', 'data', 'preco', 'taxas', 'id_carteira', 'aquisicao_via']
    df['data'] = df['data'].dt.date
    df['valor'] = df.apply(lambda row: calcula_valor(row.qtd, row.preco), axis=1)
    df['qtd_ajustada'] = df.apply(lambda row: calculate_add(row), axis=1)

    return df


def calcula_custodia(df, data=None):

    custodia = []

    if data:
        df = df.loc[df['data'] <= data, :]

    precos_medios_de_compra = calcula_precos_medio_de_compra(df, data)

    for ticker in df['ticker'].unique():
        qtd_em_custodia = df.loc[df['ticker'] == ticker]['qtd_ajustada'].sum()
        preco_atual = busca_preco_atual(ticker)
        valor = preco_atual * qtd_em_custodia
        preco_medio_de_compra = precos_medios_de_compra[ticker]['valor']
        data_primeira_compra = precos_medios_de_compra[ticker]['data_primeira_compra']
        valorizacao = preco_atual / preco_medio_de_compra * 100.0 - 100.0
        valorizacao = "{0:.2f}".format(valorizacao)

        custodia.append({'ticker': ticker,
                         'tipo': tipo_ticker(ticker).name,
                         'qtd': qtd_em_custodia,
                         'preco_medio_compra': preco_medio_de_compra,
                         'valor': valor,
                         'preco_atual': preco_atual,
                         'valorizacao': valorizacao,
                         'data_primeira_compra': data_primeira_compra})

    df_custodia = pd.DataFrame(custodia)
    df_custodia = df_custodia.sort_values(by=['valor'], ascending=False)

    return df_custodia


def calcula_precos_medio_de_compra(df, data=None):

    precos_medios_de_compra = {}

    if data:
        df = df.loc[df['data'] <= data, :]

    df = df.sort_values(by=['data'])

    for ticker in df['ticker'].unique():
        df_ticker = df.loc[df['ticker'] == ticker].copy()
        df_ticker['cum_qtd'] = df_ticker['qtd_ajustada'].cumsum()

        df_ticker['ciclo'] = df_ticker.cum_qtd.eq(0).shift().cumsum().fillna(0)  # give back the group id for each trading circle.*

        def calc(group):
            qtd_comprada = float(group.qtd.sum())
            valor_pago = float(group.valor.sum())
            if qtd_comprada == 0:
                return None
            return valor_pago / qtd_comprada

        ultimo_ciclo = df_ticker.ciclo.max()
        df_ticker_ultimo_ciclo = df_ticker.loc[df_ticker.ciclo == ultimo_ciclo]
        df_ticker_ultimo_ciclo = df_ticker_ultimo_ciclo.loc[df_ticker_ultimo_ciclo.qtd_ajustada > 0]  # kick out the selling action
        data_primeira_compra = df_ticker_ultimo_ciclo['data'].min()
        preco_medio_de_compra = calc(df_ticker_ultimo_ciclo)
        precos_medios_de_compra[ticker] = {'valor': preco_medio_de_compra, 'data_primeira_compra': data_primeira_compra}

    return precos_medios_de_compra


def vendas_no_mes(df, ano, mes):

    vendas_no_mes = []

    df = df.copy()
    primeiro_dia_proximo_mes = (datetime.datetime(ano, mes, 1, 1, 0, 0) + relativedelta(months=1)).date()

    precos_medios_de_compra = calcula_precos_medio_de_compra(df, primeiro_dia_proximo_mes)

    date_mask = df['data'].map(lambda x: str(x.year) + '_' + str(x.month)) == str(ano) + '_' + str(mes)
    df = df[date_mask]

    df = df.loc[df.qtd_ajustada < 0, :]

    for ticker in df['ticker'].unique():
        df_vendas_ticker = df.loc[df['ticker'] == ticker, :]

        qtd_vendida = df_vendas_ticker['qtd'].sum()
        preco_medio_venda = df_vendas_ticker['valor'].sum() / qtd_vendida
        preco_medio_compra = precos_medios_de_compra[ticker]['valor']
        if preco_medio_compra:
            resultado_apurado = (preco_medio_venda - preco_medio_compra) * qtd_vendida
        else:
            resultado_apurado = None

        vendas_no_mes.append({'ticker': ticker,
                              'qtd_vendida': qtd_vendida,
                              'preco_medio_venda': preco_medio_venda,
                              'preco_medio_compra': preco_medio_compra,
                              'resultado_apurado': resultado_apurado})

    return vendas_no_mes


def tipo_ticker(ticker):
    from  src.crawler_brinvesting_etfs import e_tipo_etf
    from src.crawler_funds_explorer_bs4 import e_tipo_fii
    from src.domain.tipo_ticker import TipoTicker

    if e_tipo_fii(ticker):
        return TipoTicker.FII

    if e_tipo_etf(ticker):
        return TipoTicker.ETF

    try:
        busca_preco_atual(ticker)
        return TipoTicker.ACAO
    except:
        pass

    return None


def merge_operacoes(df, other_df):
    if not len(df) and not len(other_df):
        return pd.DataFrame(columns=colunas_obrigatorias())

    df = df.copy()

    ultima_data = datetime.date.min

    if len(df):
        ultima_data = df[df['aquisicao_via'].str.upper() == 'HomeBroker'.upper()]['data'].max()

    if len(other_df):
        df = df.append(other_df.loc[other_df['data'] > ultima_data, :], sort=False)

    df = df.sort_values(by=['data'], ascending=False)
    return df


def df_to_csv(df, filepath):
    import csv
    df = df.copy()
    df['data'] = df['data'].apply(lambda data: data.strftime('%d/%m/%y'))
    df['id_carteira'] = pd.to_numeric(df['id_carteira'], downcast='integer')
    df.to_csv(path_or_buf=filepath,
              columns=colunas_obrigatorias(),
              sep='\t',
              quoting=csv.QUOTE_NONE,
              float_format='%.3f',
              header=False, index=False)