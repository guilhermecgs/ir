import pandas as pd
from pathlib import Path
from src.comuns_b3 import ComunsB3


class ImportadorNegociacaoB3(ComunsB3):
    COLUNA_CODIGO_NEGOCIACAO = 'Código de Negociação'
    COLUNA_COMPRA_VENDA = 'Tipo de Movimentação'
    COLUNA_QUANTIDADE = 'Quantidade'
    COLUNA_DATA_NEGOCIO = 'Data do Negócio'
    COLUNA_PRECO = 'Preço'
    COLUNA_VALOR = 'Valor'
    COLUNA_MERCADO = 'Mercado'
    COLUNA_PRAZO_VENCIMENTO = 'Prazo/Vencimento'
    COLUNA_INSTITUICAO = 'Instituição'

    def busca_trades(self, pasta_arquivos: str):
        basepath = Path(pasta_arquivos)
        files_in_basepath = basepath.iterdir()
        dfs = []
        for item in files_in_basepath:
            if item.is_file() and item.suffix == '.xlsx':
                dfs.append(self.__importar_movimentacoes(item.as_posix()))
        return pd.concat(dfs)

    def __importar_movimentacoes(self, caminhoArquivoXlsx: str):
        df = pd.read_excel(caminhoArquivoXlsx)

        # Valida que as colunas no arquivo são as esperadas
        colunas_arquivo = df.head().columns.to_list()
        for coluna in self.__lista_colunas_obrigatorias():
            if coluna not in colunas_arquivo:
                raise Exception(f"Coluna obrigatória não está presente no arquivo {caminhoArquivoXlsx} [{coluna}].")

        mapeamento_colunas = {self.COLUNA_CODIGO_NEGOCIACAO: 'ticker',
                              self.COLUNA_COMPRA_VENDA: 'operacao',
                              self.COLUNA_QUANTIDADE: 'qtd',
                              self.COLUNA_DATA_NEGOCIO: 'data',
                              self.COLUNA_PRECO: 'preco',
                              self.COLUNA_VALOR: 'valor'}
        colunas_remover = [self.COLUNA_MERCADO, 
                           self.COLUNA_PRAZO_VENCIMENTO,
                           self.COLUNA_INSTITUICAO]
        return self.converte_dataframe_para_formato_padrao(df, mapeamento_colunas, colunas_remover)

    def __lista_colunas_obrigatorias(self):
        return [
            self.COLUNA_CODIGO_NEGOCIACAO,
            self.COLUNA_COMPRA_VENDA,
            self.COLUNA_QUANTIDADE,
            self.COLUNA_DATA_NEGOCIO,
            self.COLUNA_PRECO,
            self.COLUNA_VALOR
        ]