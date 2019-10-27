import dropbox

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

    df['add'] = df.apply(lambda row: calculate_add(row), axis=1)

    return df


def calcula_custodia(df):

    custodia = []

    for ticker in df['ticker'].unique():
        ticker_na_carteira = df.loc[df['ticker'] == ticker]['add'].sum()
        custodia.append({'ticker': ticker, 'qtd': ticker_na_carteira})

    custodia = pd.DataFrame(custodia)

    return custodia