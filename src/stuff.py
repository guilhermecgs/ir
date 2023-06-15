import datetime
import pandas as pd
import numpy as np
from tqdm import tqdm
from cachier import cachier

from src.dataframe_hash import _hash_params
from src.dropbox_files import OPERATIONS_FILEPATH
from src.preco_atual import busca_preco_atual
from src.tipo_ticker import tipo_ticker
from src.crawler_funds_explorer_bs4 import fii_dividend_yield


def todas_as_colunas():
    result = colunas_obrigatorias()
    result.extend(['valor', 'qtd_ajustada'])
    return result


def colunas_obrigatorias():
    return ['ticker', 'operacao', 'qtd', 'data', 'preco', 'taxas', 'aquisicao_via']


def calcula_valor(qtd, preco):
    return abs(qtd) * preco


def calculate_add(row):
    if row['operacao'] == 'Compra':
        return row['qtd']
    else:
        return row['qtd'] * -1


def get_operations(filepath=None):
    if not filepath:
        filepath = OPERATIONS_FILEPATH

    try:
        df = pd.read_csv(filepath, delim_whitespace=True,
                         header=None,
                         parse_dates=[3],
                         dayfirst=True)
    except:
        return pd.DataFrame(columns=todas_as_colunas())

    try:
        df.columns = colunas_obrigatorias()
    except:
        columns = colunas_obrigatorias()
        columns.insert(6, 'id_carteira')
        df.columns = columns
        df = df.drop(['id_carteira'], axis=1)

    if len(df):
        df['data'] = df['data'].dt.date
        df['valor'] = df.apply(lambda row: calcula_valor(float(row.qtd), float(row.preco)), axis=1)
        df['qtd_ajustada'] = df.apply(lambda row: calculate_add(row), axis=1)
    else:
        return pd.DataFrame(columns=todas_as_colunas())

    return df


def calcula_custodia(df, data=None):

    custodia = []

    if not data:
        data = datetime.date.today()

    df = df.loc[df['data'] <= data, :]

    for ticker in (pbar := tqdm(df['ticker'].unique(), desc='Processamento de tickers ')):
        pbar.set_description("Processing ticker: %s" % ticker)
        pbar.refresh()
        
        qtd_em_custodia = df.loc[df['ticker'] == ticker]['qtd_ajustada'].sum()
        if qtd_em_custodia > 0:
            pbar.set_description("Processing ticker: %s , fetching data..." % ticker)
            try:
                preco_atual = float('nan')
                try:
                    preco_atual = busca_preco_atual(ticker)
                except:
                    pass
                valor = preco_atual * qtd_em_custodia
                preco_medio_de_compra = calcula_preco_medio_de_compra(df, ticker, data)
                valor_preco_medio_de_compra = preco_medio_de_compra['valor']
                data_primeira_compra = preco_medio_de_compra['data_primeira_compra']

                if valor_preco_medio_de_compra <= 0.0001:
                    valorizacao = 'NA'  # ex: direitos de compra com custo zero
                else:
                    valorizacao = preco_atual / valor_preco_medio_de_compra * 100.0 - 100.0
                    valorizacao = "{0:.2f}".format(valorizacao)

                custodia.append({'ticker': ticker,
                                 'tipo': tipo_ticker(ticker).name,
                                 'qtd': int(qtd_em_custodia),
                                 'preco_medio_compra': valor_preco_medio_de_compra,
                                 'valor': valor,
                                 'preco_atual': preco_atual,
                                 'valorizacao': valorizacao,
                                 'ultimo_yield': fii_dividend_yield(ticker),
                                 'data_primeira_compra': data_primeira_compra})
            except Exception as ex:
                raise Exception('Erro ao calcular custodia do ticker {}'.format(ticker), ex)
        pbar.set_description("Processed ticker: %s" % ticker)

    df_custodia = pd.DataFrame(custodia)
    df_custodia = df_custodia.sort_values(by=['valor'], ascending=False)

    return df_custodia


def check_tipo_ticker(df):
    for ticker in (pbar := tqdm(df['ticker'].unique(), desc='Verificando tipo de cada ticker ')):
        pbar.set_description("Processing ticker: %s" % ticker)
        pbar.refresh()

        if not tipo_ticker(ticker):
            raise Exception("Não foi possível descobrir o tipo do ticker: %s" % ticker)

        pbar.set_description("Processed ticker: %s" % ticker)


@cachier(stale_after=datetime.timedelta(hours=1), hash_params=_hash_params)
def calcula_precos_medios_de_compra(df, ticker):
    df = df.sort_values(by=['data'])

    df['is_compra'] = df['qtd_ajustada'] >= 0
    df = df.sort_values(by=['data', 'is_compra'], ascending=[True, False])
    df = df.drop(['is_compra'], axis=1)

    df_ticker = df.loc[df['ticker'] == ticker].copy()
    df_ticker = df_ticker.reset_index(drop=True)
    df_ticker['cum_qtd'] = df_ticker['qtd_ajustada'].cumsum()
    df_ticker['ciclo'] = df_ticker.cum_qtd.eq(0).shift().cumsum().fillna(0)

    df_ticker['cum_qtd_anterior'] = df_ticker['cum_qtd'].shift(1, fill_value=0)
    df_ticker['preco_medio_compra'] = np.nan
    for i, row in df_ticker.iterrows():
        if row['qtd_ajustada'] > 0:
            preco_medio_compra_atual = df_ticker['preco_medio_compra'].shift(1, fill_value=df_ticker['preco'].iloc[0])[i]
            cum_qtd_anterior = df_ticker['cum_qtd_anterior'][i]
            valor_da_compra_atual = row['valor']
            preco_medio_compra = (valor_da_compra_atual + preco_medio_compra_atual * cum_qtd_anterior) / df_ticker['cum_qtd'][i]
            df_ticker.iloc[i, df_ticker.columns == 'preco_medio_compra'] = preco_medio_compra
        else:
            try:
                df_ticker.iloc[i, df_ticker.columns == 'preco_medio_compra'] = df_ticker['preco_medio_compra'][i - 1]
            except:
                pass

    return df_ticker


def calcula_preco_medio_de_compra(df, ticker, data):
    df_ticker = calcula_precos_medios_de_compra(df, ticker)
    compra_anterior_a_data = df_ticker.loc[df_ticker['data'] <= data, :].iloc[-1]
    ciclo = compra_anterior_a_data['ciclo']
    data_primeira_compra_do_ciclo = df_ticker.loc[df_ticker['ciclo'] == ciclo]['data'].min()
    return {'valor': compra_anterior_a_data['preco_medio_compra'], 'data_primeira_compra': data_primeira_compra_do_ciclo}


def merge_operacoes(df, other_df):
    assert df is not None
    assert other_df is not None

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
    df.to_csv(path_or_buf=filepath,
              columns=colunas_obrigatorias(),
              sep='\t',
              quoting=csv.QUOTE_NONE,
              float_format='%.3f',
              header=False, index=False)


def compras_no_mes(df, ano, mes):

    compras_no_mes = []

    df = df.copy()
    date_mask = df['data'].map(lambda x: str(x.year) + '_' + str(x.month)) == str(ano) + '_' + str(mes)
    df = df[date_mask]

    df = df.loc[df.qtd_ajustada > 0, :]

    for ticker in df['ticker'].unique():
        df_compras_ticker = df.loc[df['ticker'] == ticker, :]

        qtd_comprada = df_compras_ticker['qtd'].sum()
        preco_medio_compra = df_compras_ticker['valor'].sum() / qtd_comprada

        compras_no_mes.append({'ticker': ticker,
                               'qtd_comprada': qtd_comprada,
                               'preco_medio_compra': preco_medio_compra})

    return compras_no_mes


def vendas_no_mes(df, ano, mes):

    vendas_no_mes = []

    def date_mask_fn(data):
        return str(data.year) + '_' + str(data.month) == str(ano) + '_' + str(mes)

    tickers_vendidos_no_mes = df[df['data'].map(date_mask_fn)].loc[df.qtd_ajustada < 0, :]['ticker'].unique()
    for ticker in tickers_vendidos_no_mes:
        df_ticker = calcula_precos_medios_de_compra(df, ticker)
        df_ticker = df_ticker[df_ticker['data'].map(date_mask_fn)]
        df_ticker = df_ticker.loc[df_ticker.qtd_ajustada < 0, :]

        for preco_medio_compra, df_ticker_vendas in df_ticker.groupby(by=['preco_medio_compra']):
            qtd_vendida = df_ticker_vendas['qtd'].sum()
            preco_medio_venda = df_ticker_vendas['valor'].sum() / qtd_vendida
            resultado_apurado = (preco_medio_venda - preco_medio_compra) * qtd_vendida

            vendas_no_mes.append({'ticker': ticker,
                                  'qtd_vendida': qtd_vendida,
                                  'preco_medio_venda': preco_medio_venda,
                                  'preco_medio_compra': preco_medio_compra,
                                  'resultado_apurado': resultado_apurado})

    return vendas_no_mes
