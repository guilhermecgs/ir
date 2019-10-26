import dropbox

import pandas as pd

df = pd.read_csv('/Users/guilhermesilveira/Dropbox/Finance/operacoes/gcgs/export_operacoes_gcgs.txt', sep='\t', header=None)

df

df.columns = ['ID', 'OPERACAO', 'QUANTIDADE', 'DATA', 'PRECO', 'TAXAS', 'ID_CARTEIRA']

df['DATA'] = pd.to_datetime(df['DATA'], format('%Y/%m/%d'))

pass
