import os
import datetime
from tabulate import tabulate
from src.stuff import calcula_custodia
from src.tipo_ticker import TipoTicker
from pretty_html_table import build_table
import pandas as pd


def __tab(tamanho):
    return str('\t' * tamanho)


def __format(float_value):
    return 'R$ ' + '{:.2f}'.format(float_value)


def relatorio_txt(ir):
    relatorio = []
    relatorio.append('RELATORIO')
    relatorio.append('')
    relatorio.append('Custódia')
    custodia = calcula_custodia(ir.df, datetime.datetime.now().date())
    columns = ['ticker', 'qtd', 'valor', 'preco_atual', 'preco_medio_compra', 'valorizacao', 'ultimo_yield', 'tipo', 'data_primeira_compra']
    headers = ['ticker', 'qtd', 'valor (R$)', 'Preco Atual (R$)', 'Preco Medio Compra (R$)', 'valorizacao (%)', 'Ultimo Yield [%]', 'tipo', 'Dt.Compra']
    custodia = custodia[columns]
    custodia = custodia[custodia.valor > 0]
    total_na_carteira = custodia['valor'].sum()
    custodia['valorizacao'] = custodia.apply(lambda row: '{:.2f}'.format(float(row.valorizacao)), axis=1)
    custodia['valor'] = custodia.apply(lambda row: '{:.2f}'.format(row.valor), axis=1)
    custodia['preco_atual'] = custodia.apply(lambda row: '{:.2f}'.format(row.preco_atual), axis=1)
    custodia['preco_medio_compra'] = custodia.apply(lambda row: '{:.2f}'.format(row.preco_medio_compra), axis=1)
    custodia['ultimo_yield'] = custodia.apply(lambda row: '' if row.ultimo_yield is None else '{:.2f}'.format(row.ultimo_yield), axis=1)
    relatorio.append(tabulate(custodia, showindex=False, headers=headers, tablefmt='psql'))
    relatorio.append('Total na carteira : ' + __format(total_na_carteira))

    for data in ir.datas:
        if ir.possui_vendas_no_mes(data):
            relatorio.append('')
            relatorio.append(__tab(1) + 'MES : ' + str(data.month) + '/' + str(data.year))
            relatorio.append(__tab(1) + 'Vendas:')

            vendas_no_mes_por_tipo = ir.get_vendas_no_mes_por_tipo(data)
            for tipo in TipoTicker:
                if len(vendas_no_mes_por_tipo[tipo]):
                    relatorio.append(__tab(2) + tipo.name + ':')
                    df_mes_por_tipo = pd.DataFrame(columns=['ticker', 'Qtd Vendida [#]', 'Preco Médio de Compra [R$]', 'Preco Médio de Venda [R$]', 'Resultado Apurado [R$]'])

                    for venda in vendas_no_mes_por_tipo[tipo]:
                        df_mes_por_tipo.loc[len(df_mes_por_tipo)] = [venda['ticker'],
                                                                     str(int(venda['qtd_vendida'])),
                                                                     __format(venda['preco_medio_compra']),
                                                                     __format(venda['preco_medio_venda']),
                                                                     __format(venda['resultado_apurado'])]

                    relatorio.append(__tab(3) + tabulate(df_mes_por_tipo, headers=df_mes_por_tipo.columns, showindex=False, tablefmt='psql').replace('\n', '\n' + __tab(3)))
                    relatorio.append(__tab(3) + 'Lucro/Prejuizo no mês: ' + __format(ir.calcula_prejuizo_por_tipo(data, tipo)))
                    relatorio.append(__tab(3) + 'Lucro/Prejuizo acumulado: ' + __format(ir.calcula_prejuizo_acumulado(data, tipo)))
                    relatorio.append(__tab(3) + 'IR no mês para ' + tipo.name + ': ' + __format(ir.calcula_ir_a_pagar(ir.calcula_prejuizo_acumulado(data, tipo), tipo)))

            relatorio.append(__tab(2) + 'Dedo-Duro TOTAL no mês: ' + __format(ir.calcula_dedo_duro_no_mes(data)))
            relatorio.append(__tab(2) + 'IR a pagar TOTAL no mês: ' + __format(ir.calcula_ir_a_pagar_no_mes(data)))

    return '\n'.join(relatorio)


def relatorio_html(ir):
    relatorio = '<html>'
    relatorio += __h1('RELATORIO')
    relatorio += __p('')
    relatorio += __h2('Custódia')
    custodia = calcula_custodia(ir.df, datetime.datetime.now().date())
    custodia = custodia[custodia.valor > 0]
    total_na_carteira = custodia['valor'].sum()
    custodia['valorizacao'] = custodia.apply(lambda row: '{:.2f}'.format(float(row.valorizacao)), axis=1)
    custodia['valor'] = custodia.apply(lambda row: '{:.2f}'.format(row.valor), axis=1)
    custodia['preco_atual'] = custodia.apply(lambda row: '{:.2f}'.format(row.preco_atual), axis=1)
    custodia['preco_medio_compra'] = custodia.apply(lambda row: '{:.2f}'.format(row.preco_medio_compra), axis=1)
    custodia['ultimo_yield'] = custodia.apply(lambda row: '' if row.ultimo_yield is None else '{:.2f}'.format(row.ultimo_yield), axis=1)
    headers = ['ticker', 'qtd', 'valor (R$)', 'Preco Atual (R$)', 'Preco Medio Compra (R$)', 'valorizacao (%)', 'Ultimo Yield [%]', 'tipo', 'Dt.Compra']
    columns = ['ticker', 'qtd', 'valor', 'preco_atual', 'preco_medio_compra', 'valorizacao', 'ultimo_yield', 'tipo', 'data_primeira_compra']
    custodia = custodia[columns]
    custodia.columns = headers
    relatorio += build_table(custodia, __cor_tabela())
    relatorio += __p('Total na carteira : ' + __format(total_na_carteira))
    relatorio += __hr()

    for data in ir.datas:
        if ir.possui_vendas_no_mes(data):

            relatorio += __p('')
            relatorio += __h3('MES : ' + str(data.month) + '/' + str(data.year))
            relatorio += __p('Vendas:', tab=1)

            vendas_no_mes_por_tipo = ir.get_vendas_no_mes_por_tipo(data)
            for tipo in TipoTicker:
                if len(vendas_no_mes_por_tipo[tipo]):
                    relatorio += __p(tipo.name + ':', tab=2)
                    df_mes_por_tipo = pd.DataFrame(columns=['ticker', 'Qtd Vendida [#]', 'Preco Médio de Compra [R$]', 'Preco Médio de Venda [R$]', 'Resultado Apurado [R$]'])

                    for venda in vendas_no_mes_por_tipo[tipo]:
                        df_mes_por_tipo.loc[len(df_mes_por_tipo)] = [venda['ticker'],
                                                                     str(int(venda['qtd_vendida'])),
                                                                     __format(venda['preco_medio_compra']),
                                                                     __format(venda['preco_medio_venda']),
                                                                     __format(venda['resultado_apurado'])]

                    relatorio += __p(build_table(df_mes_por_tipo, __cor_tabela(tipo)), tab=3)
                    relatorio += __p('Lucro/Prejuizo no mês: ' + __format(ir.calcula_prejuizo_por_tipo(data, tipo)), tab=3)
                    relatorio += __p('Lucro/Prejuizo acumulado: ' + __format(ir.calcula_prejuizo_acumulado(data, tipo)), tab=3)
                    relatorio += __p('IR no mês para ' + tipo.name + ': ' + __format(ir.calcula_ir_a_pagar(ir.calcula_prejuizo_acumulado(data, tipo), tipo)), tab=3)

            relatorio += __p('Dedo-Duro TOTAL no mês: ' + __format(ir.calcula_dedo_duro_no_mes(data)), tab=2)
            relatorio += __p('IR a pagar TOTAL no mês: ' + __format(ir.calcula_ir_a_pagar_no_mes(data)), tab=2)
            relatorio += __hr()

    relatorio += __close_html()
    return ''.join(relatorio)


def assunto(ir):
    assunto = ''

    if ir.calcula_ir_a_pagar_no_mes(ir.datas[-1]) > 0.0:
        assunto = 'IMPOSTO A PAGAR! - '

    assunto = assunto + 'Calculo de IR - ' + ir.mes_do_relatorio + ' - CPF: ' + os.environ['CPF'] + ' - ' \
              + datetime.datetime.now().strftime("%H:%M:%S")

    return assunto


def __init_html():
    return '<html>' \
           '    <head>' \
           '        <meta name="viewport" content="width=device-width" />' \
           '        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />' \
           '    </head>'  \
           '    <body class="">'


def __close_html():
    return '    </body></html>'


def __cor_tabela(tipo=None):
    if tipo is None:
        return 'blue_light'
    elif tipo == TipoTicker.ACAO:
        return 'grey_light'
    elif tipo == TipoTicker.FII:
        return 'yellow_light'
    elif tipo == TipoTicker.ETF:
        return 'orange_light'
    return 'blue_light'


def __hr():
    return '<hr/>'


def __p(text, tab=None):
    style = ''
    if tab:
        padding = tab * 30
        style = ' style="padding-left: ' + str(padding) + 'px;" '

    if '<p' in text:
        return text.replace('<p', '<p' + style)
    else:
        return '<p' + style + '>' + text + '</p>'


def __h1(text):
    return '<h1>' + text + '</h1>'


def __h2(text):
    return '<h2>' + text + '</h2>'


def __h3(text):
    return '<h3>' + text + '</h3>'
