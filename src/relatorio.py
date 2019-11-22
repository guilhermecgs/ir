from src.tipo_ticker import TipoTicker
from src.stuff import calcula_custodia


def __tab(tamanho):
    return ' ' * tamanho * 4


def __format(float_value):
    return 'R$ ' + '{:.2f}'.format(float_value)


def report_txt(ir):

    print('RELATORIO')
    print('')

    print('Custódia')
    custodia = calcula_custodia(ir.df)
    print(custodia[custodia.valor > 0].to_string(columns=['ticker',
                                                          'qtd',
                                                          'valor',
                                                          'preco_atual',
                                                          'preco_medio_compra',
                                                          'valorizacao',
                                                          'tipo',
                                                          'data_primeira_compra'],
                                                 index=False))
    print('Total na carteira : ' + __format(custodia['valor'].sum()))

    for data in ir.datas:
        if ir.possui_vendas_no_mes(data):
            print('')
            print(__tab(1) + 'MES : ' + str(data.month) + '/' + str(data.year))
            print(__tab(2) + 'Vendas:')

            vendas_no_mes_por_tipo = ir.get_vendas_no_mes_por_tipo(data)
            for tipo in TipoTicker:
                if len(vendas_no_mes_por_tipo[tipo]):
                    print(__tab(3) + tipo.name + ':')
                    for venda in vendas_no_mes_por_tipo[tipo]:
                        print(__tab(4) + str(venda))

                    print(__tab(4) + 'Lucro/Prejuizo no mês: ' + __format(ir.calcula_prejuizo_por_tipo(data, tipo)))
                    print(__tab(4) + 'Lucro/Prejuizo acumulado: ' + __format(ir.calcula_prejuizo_acumulado(data, tipo)))
                    print(__tab(4) + 'IR no mês para ' + tipo.name + ': ' + __format(ir.calcula_ir_a_pagar(ir.calcula_prejuizo_acumulado(data, tipo), tipo)))

            print(__tab(3) + 'IR a pagar TOTAL no mês: ' + __format(ir.calcula_ir_a_pagar_no_mes(data)))
