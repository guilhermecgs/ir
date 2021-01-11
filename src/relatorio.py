import os
import datetime
from dateutil.relativedelta import relativedelta
from tabulate import tabulate
from src.stuff import calcula_custodia
from src.tipo_ticker import TipoTicker
from pretty_html_table import build_table
from src.dados import ticker_nome, ticker_cnpj, ticker_codigo_irpf, ticker_data
import pandas as pd

#
# Para não ficar mostrando todo o detalhamento de vendas 
# limita a apresentacao no relatorio aos ultimos meses
#
meses_detalhamento_vendas = int(os.getenv("MESES_VENDAS","6"))

def __tab(tamanho):
    return str('\t' * tamanho)


def __format(float_value):
    return 'R$ ' + '{:.2f}'.format(float_value)

#
# Calcula totais por tipo de ativo 
#
def calcula_totais(custodia):
    totais = custodia.groupby('tipo', as_index=False, sort=False).agg({ 'valor' : [ 'sum', 'count' ], 'valor_original' : 'sum'} )
    totais.columns = ['tipo', 'valor', 'ativos', 'valor_original']
    total_na_carteira = totais['valor'].sum()
    totais = totais.append(pd.DataFrame({ 'tipo' : [ 'TOTAL' ], 
        'valor' : [ total_na_carteira ], 
        'ativos' : [ totais['ativos'].sum() ], 
        'valor_original' : [ totais['valor_original'].sum() ]   }))
    totais['saldo'] = totais.apply(lambda row: row.valor - row.valor_original, axis=1)
    totais['valorizacao'] = totais.apply(lambda row: '' if row.valor_original == 0 else '{:.2f}'.format((row.valor / row.valor_original) * 100.0 - 100.0), axis=1)
    totais['pct'] = totais.apply(lambda row: '{:.2f}'.format((row.valor / total_na_carteira) * 100), axis=1)
    totais['valor'] = totais.apply(lambda row: '{:.2f}'.format(row.valor), axis=1)
    totais['valor_original'] = totais.apply(lambda row: '{:.2f}'.format(row.valor_original), axis=1)
    totais['ativos'] = totais.apply(lambda row: '{:.0f}'.format(row.ativos), axis=1)
    totais = totais[['tipo', 'valor', 'pct', 'valor_original', 'saldo', 'valorizacao', 'ativos']]
    return totais

#
# Adiciona informações para declaração de custódia no IRPF anual
#
def adiciona_dados_irpf(custodia, dados_irpf):
    if dados_irpf:
        custodia['CNPJ'] = custodia.apply(lambda row: ticker_cnpj(row.ticker), axis=1)
        custodia['Nome'] = custodia.apply(lambda row: ticker_nome(row.ticker), axis=1)
        custodia['CNPJ Adm'] = custodia.apply(lambda row: ticker_data(row.ticker, 'cnpj_adm'), axis=1)
        custodia['Nome Adm'] = custodia.apply(lambda row: ticker_data(row.ticker, 'nome_adm'), axis=1)
        custodia['RI URL'] = custodia.apply(lambda row: ticker_data(row.ticker, 'ri_url'), axis=1)
    
def relatorio_txt(custodia, ir, data_ref, dados_irpf):
    relatorio = []
    relatorio.append('RELATORIO')
    relatorio.append('')
    relatorio.append('Custódia : ' + os.environ['CPF'] + " " + str(data_ref))    
    columns = ['ticker', 'qtd', 'valor', 'valor_original', 'preco_atual', 'preco_medio_compra', 'valorizacao', 'ultimo_yield', 'p_vp', 'tipo', 'data_primeira_compra']
    headers = ['ticker', 'qtd', 'valor (R$)', 'valor compra (R$)', 'Preco Atual (R$)', 'Preco Medio Compra (R$)', 'valorizacao (%)', 'Ultimo Yield [%]', 'P/VP', 'tipo', 'Dt.Compra']
    if dados_irpf:
        headers.append('CNPJ')
        headers.append('Nome')
        headers.append('CNPJ Adm')
        headers.append('Nome Adm')
        headers.append('RI URL')
    custodia = custodia[columns]
    custodia = custodia[custodia.valor > 0]

    totais = calcula_totais(custodia)    
    
    custodia['valorizacao'] = custodia.apply(lambda row: '{:.2f}'.format(float(row.valorizacao)), axis=1)
    custodia['valor'] = custodia.apply(lambda row: '{:.2f}'.format(row.valor), axis=1)
    custodia['valor_original'] = custodia.apply(lambda row: '{:.2f}'.format(row.valor_original), axis=1)
    custodia['preco_atual'] = custodia.apply(lambda row: '{:.2f}'.format(row.preco_atual), axis=1)
    custodia['preco_medio_compra'] = custodia.apply(lambda row: '{:.2f}'.format(row.preco_medio_compra), axis=1)
    custodia['ultimo_yield'] = custodia.apply(lambda row: '' if row.ultimo_yield is None else '{:.2f}'.format(row.ultimo_yield), axis=1)
    custodia['p_vp'] = custodia.apply(lambda row: '' if row.p_vp is None else '{:.2f}'.format(row.p_vp), axis=1)

    adiciona_dados_irpf(custodia, dados_irpf)

    relatorio.append(tabulate(custodia, showindex=False, headers=headers, tablefmt='psql'))
    
    relatorio.append(tabulate(totais, showindex=False, headers=[ "Tipo", "Valor (R$)", "% da carteira", "Valor Compra (R$)", "Saldo (R$)", "valorização (%)", "ativos" ], tablefmt='psql'))

    data_limite = data_ref - relativedelta(months=meses_detalhamento_vendas)
    for data in ir.datas:
        if ir.possui_vendas_no_mes(data) and data >= data_limite:
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
                    relatorio.append(__tab(3) + 'Lucro/Prejuizo no mês + Prejuizo acumulado: ' + __format(ir.calcula_prejuizo_acumulado(data, tipo)))
                    relatorio.append(__tab(3) + 'IR no mês para ' + tipo.name + ': ' + __format(ir.calcula_ir_a_pagar(ir.calcula_prejuizo_acumulado(data, tipo), tipo)))

            relatorio.append(__tab(2) + 'Dedo-Duro TOTAL no mês: ' + __format(ir.calcula_dedo_duro_no_mes(data)))
            relatorio.append(__tab(2) + 'IR a pagar TOTAL no mês: ' + __format(ir.calcula_ir_a_pagar_no_mes(data)))

    return '\n'.join(relatorio)


def relatorio_html(custodia, ir, data_ref, dados_irpf):
    relatorio = '<html>'
    relatorio += __h1('RELATORIO')
    relatorio += __p('')
    relatorio += __h2('Custódia ' + os.environ['CPF'] + " " + str(data_ref))
    columns = ['ticker', 'qtd', 'valor', 'valor_original', 'preco_atual', 'preco_medio_compra', 'valorizacao', 'ultimo_yield', 'p_vp', 'tipo', 'data_primeira_compra']
    custodia = custodia[columns]
    custodia = custodia[custodia.valor > 0]

    totais = calcula_totais(custodia)

    custodia['valorizacao'] = custodia.apply(lambda row: '{:.2f}'.format(float(row.valorizacao)), axis=1)
    custodia['valor'] = custodia.apply(lambda row: '{:.2f}'.format(row.valor), axis=1)
    custodia['valor_original'] = custodia.apply(lambda row: '{:.2f}'.format(row.valor_original), axis=1)
    custodia['preco_atual'] = custodia.apply(lambda row: '{:.2f}'.format(row.preco_atual), axis=1)
    custodia['preco_medio_compra'] = custodia.apply(lambda row: '{:.2f}'.format(row.preco_medio_compra), axis=1)
    custodia['ultimo_yield'] = custodia.apply(lambda row: '' if row.ultimo_yield is None else '{:.2f}'.format(row.ultimo_yield), axis=1)
    custodia.columns = ['ticker', 'qtd', 'valor (R$)', 'valor compra (R$)', 'Preco Atual (R$)', 'Preco Medio Compra (R$)', 'valorizacao (%)', 'Ultimo Yield [%]', 'P/VP', 'tipo', 'Dt.Compra']

    adiciona_dados_irpf(custodia, dados_irpf)
    relatorio += build_table(custodia, __cor_tabela())
    
    totais = totais[['tipo', 'valor', 'pct', 'valor_original', 'saldo', 'valorizacao', 'ativos']]
    totais.columns = ['Tipo', 'Valor (R$)', '% da carteira', 'Valor Compra (R$)', 'Saldo (R$)', 'valorização (%)', 'ativos' ]
    relatorio += build_table(totais, __cor_tabela())
    
    relatorio += __hr()

    data_limite = data_ref - relativedelta(months=meses_detalhamento_vendas)
    for data in ir.datas:
        if ir.possui_vendas_no_mes(data) and data > data_limite:

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
                    relatorio += __p('Lucro/Prejuizo no mês + Prejuizo acumulado: ' + __format(ir.calcula_prejuizo_acumulado(data, tipo)), tab=3)
                    relatorio += __p('IR no mês para ' + tipo.name + ': ' + __format(ir.calcula_ir_a_pagar(ir.calcula_prejuizo_acumulado(data, tipo), tipo)), tab=3)

            relatorio += __p('Dedo-Duro TOTAL no mês: ' + __format(ir.calcula_dedo_duro_no_mes(data)), tab=2)
            #TODO: talvez melhorar essa msg, pois o que FALTA pagar tem que descontar o dedo duro, o total que tem que pagar no mês é esse
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
