import pandas as pd

from src.stuff import colunas_obrigatorias, calcula_valor


def create_testing_dataframe(data):
    for row in data:
        for column in colunas_obrigatorias():
            if column not in row:
                row[column] = None

    if len(data):
        df = pd.DataFrame(data)
        df['qtd_ajustada'] = df['qtd']
        df['qtd'] = df.apply(lambda row: abs(row.qtd), axis=1)
        df['valor'] = df.apply(lambda row: calcula_valor(row.qtd, row.preco), axis=1)
    else:
        df = pd.DataFrame(columns=colunas_obrigatorias())

    return df