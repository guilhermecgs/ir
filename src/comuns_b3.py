import pandas as pd

class ComunsB3():

    def converte_dataframe_para_formato_padrao(self, df, mapeamento_colunas: dict, colunas_remover: list):
        df = df.rename(columns=mapeamento_colunas)

        from src.stuff import calculate_add

        def formata_compra_venda(operacao):
            if operacao in ['Venda', 'Compra']:
                return operacao
            if operacao == 'V':
                return 'Venda'
            else:
                return 'Compra'

        def remove_fracionado_ticker(ticker):
            return ticker[:-1] if ticker.endswith('F') else ticker

        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        df['data'] = df['data'].dt.date
        df['ticker'] = df.apply(lambda row: remove_fracionado_ticker(row.ticker), axis=1)
        df['operacao'] = df.apply(lambda row: formata_compra_venda(row.operacao), axis=1)
        df['qtd_ajustada'] = df.apply(lambda row: calculate_add(row), axis=1)

        df['taxas'] = 0.0
        df['aquisicao_via'] = 'HomeBroker'

        df.drop(columns=colunas_remover, inplace=True)
        return df