import pandas as pd

from src.dropbox_files import OPERATIONS_FILEPATH


def get_operations_dataframe():
    df = pd.read_csv(OPERATIONS_FILEPATH, sep='\t',
                     header=None,
                     parse_dates=[3])

    df.columns = ['ticker', 'operacao', 'qtd', 'data', 'preco', 'taxas', 'id_carteira']

    def calculate_add(row):
        if row['operacao'] == 'Compra':
            return row['qtd']
        else:
            return row['qtd'] * -1

    df['qtd'] = df.apply(lambda row: calculate_add(row), axis=1)

    return df


def calcula_custodia(df):

    custodia = []

    for ticker in df['ticker'].unique():
        ticker_na_carteira = df.loc[df['ticker'] == ticker]['add'].sum()
        custodia.append({'ticker': ticker, 'qtd': ticker_na_carteira})

    df_custodia = pd.DataFrame(custodia)
    df_custodia = df_custodia.sort_values(by=['qtd'], ascending=False)

    return df_custodia


def calcula_precos_medio_de_compra(df):

    df = df.sort_values(by=['data'])

    precos_medios_de_compra = {}

    for ticker in df['ticker'].unique():

        df_ticker = df.loc[df['ticker'] == ticker]
        df_ticker['valor'] = df_ticker['qtd'] * df_ticker['preco']
        df_ticker['cum_qtd'] = df_ticker['qtd'].cumsum()

        df_ticker['ciclo'] = df_ticker.cum_qtd.eq(0).shift().cumsum().fillna(0)  # give back the group id for each trading circle.*

        def calc(group):
            qtd_comprada = float(group.qtd.sum())
            valor_pago = float(group.valor.sum())
            return valor_pago / qtd_comprada

        ultimo_ciclo = df_ticker.ciclo.max()
        df_ticker_ultimo_ciclo = df_ticker.loc[df_ticker.ciclo == ultimo_ciclo]
        df_ticker_ultimo_ciclo = df_ticker_ultimo_ciclo.loc[df_ticker_ultimo_ciclo.qtd > 0]  # kick out the selling action
        preco_medio_de_compra = calc(df_ticker_ultimo_ciclo)
        precos_medios_de_compra[ticker] = preco_medio_de_compra

    return precos_medios_de_compra

