import os
import datetime
from dateutil.relativedelta import relativedelta
from tabulate import tabulate
from src.stuff import calcula_custodia
from src.tipo_ticker import TipoTicker
from pretty_html_table import build_table
from src.dados import ticker_nome, ticker_cnpj, ticker_codigo_irpf, ticker_data
import pandas as pd
import numpy as np

#
# Para não ficar mostrando todo o detalhamento de vendas 
# limita a apresentacao no relatorio aos ultimos meses
#
meses_detalhamento_vendas = int(os.getenv("MESES_VENDAS","6"))




    
def relatorio_txt(custodia, ir, data_ref, dados_irpf):
    r = RelatorioTexto()
    return r.gera_relatorio(custodia, ir, data_ref, dados_irpf)
    


def relatorio_html(custodia, ir, data_ref, dados_irpf):
    r = RelatorioHtml()
    return r.gera_relatorio(custodia, ir, data_ref, dados_irpf)


def assunto(ir):
    assunto = ''

    if ir.calcula_ir_a_pagar_no_mes(ir.datas[-1]) > 0.0:
        assunto = 'IMPOSTO A PAGAR! - '

    assunto = assunto + 'Calculo de IR - ' + ir.mes_do_relatorio + ' - CPF: ' + os.environ['CPF'] + ' - ' \
              + datetime.datetime.now().strftime("%H:%M:%S")

    return assunto

def adiciona_coluna_adicional(custodia, nome_coluna, atributo):
    if (len(nome_coluna) > 0) and (len(atributo) > 0) and not (nome_coluna in custodia.columns):
        custodia[nome_coluna] = custodia.apply(lambda row: ticker_data(row.ticker, atributo), axis=1)
        # Verifica se tem algum valor, caso não tenha remove para não ocupar espaço sem necessidade
        if len(custodia[nome_coluna].dropna()) == 0:
           custodia = custodia.drop([nome_coluna], axis=1)
    return custodia
    
#
# Adiciona informações para declaração de custódia no IRPF anual
#
def adiciona_dados_irpf(custodia, dados_irpf):
    if dados_irpf:
        for n in os.getenv('RELATORIO_COLUNAS_IRPF','cnpj-nome-cnpj_adm-nome_adm-ri_url').split('-'):
            custodia = adiciona_coluna_adicional(custodia, n, n)

def is_nan(value):
     return (value is None) or np.isnan(value)


class Relatorio:

    def to_string(self):
        return ''

    def append(self, text, tab=0):
        pass
   
    def adiciona_tabela(self, tabela, tab=0):
        pass
       
    def p(self, text, tab=None):
        self.append(text, tab=tab)
       
    def h1(self, text):
       self.append(text)


    def h2(self, text):
       self.append(text)


    def h3(self, text, tab=0):
       self.append(text, tab=tab)

    def separator(self):
       self.append('')
       self.append('')
       self.append('')

    def _format(self, float_value):
        return 'R$ ' + '{:.2f}'.format(float_value)

    def init(self):
        pass
       
    def finish(self):
        pass
       
    def adiciona_totais(self, custodia_base):
        totalizacoes = os.getenv('RELATORIO_TOTAIS','tipo-carteira:tipo')
        for s1 in totalizacoes.split('-'):
           s = s1.split(':')
           if len(s) == 2:
              totais = self.calcula_totais(custodia_base, s[0], default_column=s[1])    
           else:
              totais = self.calcula_totais(custodia_base, s[0])    
           if totais is not None:
               self.adiciona_tabela(totais)

    #
    # Calcula totais agrupados dos ativos 
    # Caso tenha somente um valor retorna None, pois não faz sentido apresentar um totalizador com uma unica linha
    #
    def calcula_totais(self, custodia, agrupador, default_column=None):
        if not agrupador in custodia.columns:
            c = custodia.copy()
            if default_column:
               if default_column not in custodia.columns:
                   c[default_column] = c.apply(lambda row: ticker_data(row.ticker, default_column, '?'), axis=1)
            c[agrupador] = c.apply(lambda row: ticker_data(row.ticker, agrupador, default_value=('?' if default_column is None else row[default_column]) ), axis=1)
            if c[agrupador].equals(c[default_column]):
                # Nao tem dados adicionais então não agrupa
                return None
            custodia = c
        totais = custodia.groupby(agrupador, as_index=False, sort=False).agg({ 'valor' : [ 'sum', 'count' ], 'valor_original' : 'sum'} )
        if len(totais) <= 1:
            return None
        
        totais.columns = [agrupador, 'valor', 'ativos', 'valor_original']
        totais = totais.sort_values("valor", ascending=False)

        total_na_carteira = totais['valor'].sum()
        totais = totais.append(pd.DataFrame({ agrupador : [ 'TOTAL' ], 
            'valor' : [ total_na_carteira ], 
            'ativos' : [ totais['ativos'].sum() ], 
            'valor_original' : [ totais['valor_original'].sum() ]   }))
        totais['saldo'] = totais.apply(lambda row: row.valor - row.valor_original, axis=1)
        totais['valorizacao'] = totais.apply(lambda row: '' if row.valor_original == 0 else '{:.2f}'.format((row.valor / row.valor_original) * 100.0 - 100.0), axis=1)
        totais['pct'] = totais.apply(lambda row: '{:.2f}'.format((row.valor / total_na_carteira) * 100), axis=1)
        totais['valor'] = totais.apply(lambda row: '{:.2f}'.format(row.valor), axis=1)
        totais['valor_original'] = totais.apply(lambda row: '{:.2f}'.format(row.valor_original), axis=1)
        totais['ativos'] = totais.apply(lambda row: '{:.0f}'.format(row.ativos), axis=1)
        totais = totais[[agrupador, 'valor', 'pct', 'valor_original', 'saldo', 'valorizacao', 'ativos']]
        totais.columns = [ agrupador, "Valor (R$)", "% da carteira", "Valor Compra (R$)", "Saldo (R$)", "valorização (%)", "ativos" ]
        return totais

    def gera_relatorio(self, custodia, ir, data_ref, dados_irpf):
        self.init()
        self.h1('RELATORIO')
        self.p('')
        self.h2('Custódia ' + os.environ['CPF'] + " " + str(data_ref))
        columns = ['ticker', 'qtd', 'valor', 'valor_original', 'preco_atual', 'preco_medio_compra', 'valorizacao', 'ultimo_yield', 'p_vp', 'tipo', 'data_primeira_compra']
        custodia = custodia[columns]
        custodia = custodia[custodia.valor > 0]

        # Salva copia antes de formatar para gerar totais
        custodia_base = custodia.copy()

        custodia['valorizacao'] = custodia.apply(lambda row: '{:.2f}'.format(float(row.valorizacao)), axis=1)
        custodia['valor'] = custodia.apply(lambda row: '{:.2f}'.format(row.valor), axis=1)
        custodia['valor_original'] = custodia.apply(lambda row: '{:.2f}'.format(row.valor_original), axis=1)
        custodia['preco_atual'] = custodia.apply(lambda row: '{:.2f}'.format(row.preco_atual), axis=1)
        custodia['preco_medio_compra'] = custodia.apply(lambda row: '{:.2f}'.format(row.preco_medio_compra), axis=1)
        custodia['ultimo_yield'] = custodia.apply(lambda row: '' if is_nan(row.ultimo_yield) else '{:.2f}'.format(row.ultimo_yield), axis=1)
        custodia['p_vp'] = custodia.apply(lambda row: '' if is_nan(row.p_vp) else '{:.2f}'.format(row.p_vp), axis=1)
        # Coloca colunas com informações adicionais
        adiciona_dados_irpf(custodia, dados_irpf)
        for n in os.getenv('RELATORIO_COLUNAS_EXTRAS','').split('-'):
            if ':' in n:
                arr = n.split(':')
                custodia = adiciona_coluna_adicional(custodia, arr[1], arr[0])
            else:
                custodia = adiciona_coluna_adicional(custodia, n, n)
        custodia = custodia.rename(columns={ 'valor' : 'valor (R$)', 
                                            'valor_original' : 'valor compra (R$)', 
                                            'preco_atual' : 'Preco Atual (R$)', 
                                            'preco_medio_compra' : 'Preco Medio Compra (R$)', 
                                            'valorizacao' : 'valorizacao (%)', 
                                            'ultimo_yeld' : 'Ultimo Yield [%]', 
                                            'p_vp' : 'P/VP', 
                                            'data_primeira_compra' : 'Dt.Compra',
                                            'nome' : 'Nome',
                                            'cnpj' : 'CNPJ',
                                            'cnpj_adm' : 'CNPJ Adm',
                                            'nome_adm' : 'Nome Administrador',
                                            'ri_url' : 'RI URL'})


        self.adiciona_tabela(custodia)
        
        self.adiciona_totais(custodia_base)
        
        self.separator()

        data_limite = data_ref - relativedelta(months=meses_detalhamento_vendas)
        for data in ir.datas:
            if ir.possui_vendas_no_mes(data) and data >= data_limite:

                self.p('')
                self.h3('MES : ' + str(data.month) + '/' + str(data.year), tab=1)
                self.p('Vendas:', tab=1)

                vendas_no_mes_por_tipo = ir.get_vendas_no_mes_por_tipo(data)
                for tipo in TipoTicker:
                    if len(vendas_no_mes_por_tipo[tipo]):
                        self.p(tipo.name + ':', tab=2)
                        df_mes_por_tipo = pd.DataFrame(columns=['ticker', 'Qtd Vendida [#]', 'Preco Médio de Compra [R$]', 'Preco Médio de Venda [R$]', 'Resultado Apurado [R$]'])

                        for venda in vendas_no_mes_por_tipo[tipo]:
                            df_mes_por_tipo.loc[len(df_mes_por_tipo)] = [venda['ticker'],
                                                                        int(venda['qtd_vendida']),
                                                                        '{:.2f}'.format(venda['preco_medio_compra']),
                                                                        '{:.2f}'.format(venda['preco_medio_venda']),
                                                                        '{:.2f}'.format(venda['resultado_apurado'])]

                        self.adiciona_tabela(df_mes_por_tipo, tab=3)
                        self.p('Lucro/Prejuizo no mês: ' + self._format(ir.calcula_prejuizo_por_tipo(data, tipo)), tab=3)
                        self.p('Lucro/Prejuizo no mês + Prejuizo acumulado: ' + self._format(ir.calcula_prejuizo_acumulado(data, tipo)), tab=3)
                        self.p('IR no mês para ' + tipo.name + ': ' + self._format(ir.calcula_ir_a_pagar(ir.calcula_prejuizo_acumulado(data, tipo), tipo)), tab=3)

                self.p('Dedo-Duro TOTAL no mês: ' + self._format(ir.calcula_dedo_duro_no_mes(data)), tab=2)
                #TODO: talvez melhorar essa msg, pois o que FALTA pagar tem que descontar o dedo duro, o total que tem que pagar no mês é esse
                self.p('IR a pagar TOTAL no mês: ' + self._format(ir.calcula_ir_a_pagar_no_mes(data)), tab=2)
                self.separator()

        self.finish()
        return self.to_string()



class RelatorioTexto(Relatorio):

   def __init__(self):
       self.relatorio = []

   def _tab(self, tamanho):
       return str('\t' * tamanho)

   def to_string(self):
       return '\n'.join(self.relatorio)
        
   def append(self, text, tab=0):
       if tab is not None and tab > 0:
          text = self._tab(tab) + text
       self.relatorio.append(text)

   def adiciona_tabela(self, tabela, tab=0):
        tb = tabulate(tabela, headers=tabela.columns, showindex=False, tablefmt='psql')
        if tab is not None and tab > 0:
            self.append(self._tab(tab) + tb.replace('\n', '\n' + self._tab(tab)) )
        else:
            self.append(tb)
        self.append('')
       
   def p(self, text, tab=None):
       self.append(text, tab=tab) 
   


def cor_tabela(tipo=None):
    if tipo is None:
        return 'blue_light'
    elif tipo == TipoTicker.ACAO:
        return 'grey_light'
    elif tipo == TipoTicker.FII:
        return 'yellow_light'
    elif tipo == TipoTicker.ETF:
        return 'orange_light'
    return 'blue_light'

class RelatorioHtml(Relatorio):

   def __init__(self):
       self.relatorio = ''
       self.useTableSorter = os.getenv('RELATORIO_HTML_TABLE_SORTER','0') == '1'

   def append(self, text, tab=0):
       self.relatorio += text

   def to_string(self):
    return ''.join(self.relatorio)
        
   def adiciona_tabela(self, tabela, tab=0):
        #TODO: Precisa alinhar corretamente pela direita as colunas numéricas e esquerda as restantes
        # Deixando tudo na direita pelo menos fica mais facil de ver os números
        self.p(build_table(tabela, cor_tabela(), text_align='right'), tab=tab)


   def _init_html(self):
       init = '<html>\n' \
              '    <head>\n' \
              '        <meta name="viewport" content="width=device-width" />\n' \
              '        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\n'
       if self.useTableSorter:
           for url in [ 'https://code.jquery.com/jquery-3.5.1.min.js',
                        'https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.3/css/theme.default.min.css',
                        'https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.3/js/jquery.tablesorter.min.js',
                        'https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.3/js/jquery.tablesorter.widgets.min.js',
                        ]:
               if url.endswith('css'):
                  init += '        <link href="' + url + '" rel="stylesheet">\n'
               else:
                  init += '        <script type="text/javascript" src="' + url + '"></script>\n'
                    
       init += '    </head>\n'

       init += '    <body class="">\n'
       if self.useTableSorter:
           init += '<script>\n' \
'$(function() {' \
' console.log("aqui");\n' \
'  $(".dataframe").tablesorter({ ' \
'	widgets: ["zebra", "filter"],' \
'                             }); ' \
'});' \
'</script>\n'
       return init


   def _close_html(self):
       return '    </body></html>\n'
       
   def separator(self):
       self.append('<hr/>')


   def p(self, text, tab=None):
       style = ''
       if tab:
           padding = tab * 30
           style = ' style="padding-left: ' + str(padding) + 'px;" '

       if '<p' in text:
           self.append(text.replace('<p', '<p' + style))
       else:
           self.append('<p' + style + '>' + text + '</p>\n')


   def _hX(self, level, text, tab=0):
        if tab > 0:
           self.p('<h1>' + text + '</h1>', tab=tab)
        else:
           self.append('<h1>' + text + '</h1>')

   def h1(self, text, tab=0):
       self._hX(1, text, tab=tab)


   def h2(self, text, tab=0):
       self._hX(2, text, tab=tab)


   def h3(self, text, tab=0):
       self._hX(3, text, tab=tab)


   def init(self):
      self.append(self._init_html())

   def finish(self):   
      self.append(self._close_html())
      
