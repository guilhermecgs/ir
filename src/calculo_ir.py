import datetime

from dateutil.relativedelta import relativedelta

from src.stuff import calcula_precos_medio_de_compra


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