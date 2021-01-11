import pandas as pd

from src.relatorio import adiciona_dados_irpf

def salva_planilha_irpf(filepath, custodia, adicionais):
    adiciona_dados_irpf(custodia, True)
    with pd.ExcelWriter(filepath) as writer:
        for tipo in custodia['tipo'].unique():
            custodia[custodia['tipo'] == tipo].to_excel(writer, sheet_name=tipo)
        for k in adicionais:
            adicionais[k].to_excel(writer, sheet_name=k)
            
        
        
    