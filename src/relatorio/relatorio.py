import datetime
from tabulate import tabulate
from src.stuff import calcula_custodia
from src.tipo_ticker import TipoTicker


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
    columns = ['ticker', 'qtd', 'valor', 'preco_atual', 'preco_medio_compra', 'valorizacao', 'tipo', 'data_primeira_compra']
    headers = ['ticker', 'qtd', 'valor (R$)', 'preco_atual (R$)', 'preco_medio_compra (R$)', 'valorizacao (%)', 'tipo', 'data_primeira_compra']
    custodia = custodia[columns]
    custodia = custodia[custodia.valor > 0]
    total_na_carteira = custodia['valor'].sum()
    custodia['valorizacao'] = custodia.apply(lambda row: '{:.2f}'.format(float(row.valorizacao)), axis=1)
    custodia['valor'] = custodia.apply(lambda row: '{:.2f}'.format(row.valor), axis=1)
    custodia['preco_atual'] = custodia.apply(lambda row: '{:.2f}'.format(row.preco_atual), axis=1)
    custodia['preco_medio_compra'] = custodia.apply(lambda row: '{:.2f}'.format(row.preco_medio_compra), axis=1)
    relatorio.append(tabulate(custodia, showindex=False, headers=headers, tablefmt='psql'))
    relatorio.append('Total na carteira : ' + __format(total_na_carteira))

    for data in ir.datas:
        if ir.possui_vendas_no_mes(data):
            relatorio.append('')
            relatorio.append(__tab(1) + 'MES : ' + str(data.month) + '/' + str(data.year))
            relatorio.append(__tab(2) + 'Vendas:')

            vendas_no_mes_por_tipo = ir.get_vendas_no_mes_por_tipo(data)
            for tipo in TipoTicker:
                if len(vendas_no_mes_por_tipo[tipo]):
                    relatorio.append(__tab(3) + tipo.name + ':')
                    for venda in vendas_no_mes_por_tipo[tipo]:
                        relatorio.append(__tab(4) + __format_venda(venda))

                    relatorio.append(__tab(4) + 'Lucro/Prejuizo no mês: ' + __format(ir.calcula_prejuizo_por_tipo(data, tipo)))
                    relatorio.append(__tab(4) + 'Lucro/Prejuizo acumulado: ' + __format(ir.calcula_prejuizo_acumulado(data, tipo)))
                    relatorio.append(__tab(4) + 'IR no mês para ' + tipo.name + ': ' + __format(ir.calcula_ir_a_pagar(ir.calcula_prejuizo_acumulado(data, tipo), tipo)))

            relatorio.append(__tab(3) + 'IR a pagar TOTAL no mês: ' + __format(ir.calcula_ir_a_pagar_no_mes(data)))

    return '\n'.join(relatorio)


def __format_venda(venda):
    return venda['ticker'] + ' - ' + __tab(1) + \
             'Qtd Vendida: ' + str(int(venda['qtd_vendida'])) + __tab(1) + \
             'Preco Médio de Compra: ' + __format(venda['preco_medio_compra']) + __tab(1) + \
             'Preco Médio de Venda: ' + __format(venda['preco_medio_venda']) + __tab(1) + \
             'Resultado Apurado: ' + __format(venda['resultado_apurado'])
