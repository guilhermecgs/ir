import unittest

from src.crawler_cei import CrawlerCei
from tabulate import tabulate
import pandas as pd
import os
import datetime


# Como o arquivo tem dados pessoais não faz parte do repositório
# Então executa o teste quando o desenvolvedor baixar o arquivo e deixar em seu ambiente com esse nome
# O teste online é habilitado quando for definida a senha de acesso CEI
HTML_CARTEIRA = 'tests_data/private_carteira_cei.html'

class TestCrawlerCei(unittest.TestCase):



    @unittest.skipUnless('SENHA_CEI' in os.environ, "sem configuracao de acesso CEI")
    def test_busca_trades(self):
        # Permite separar os arquivos de testes por CPF
        directory = os.getenv('DIR_TESTES_CEI','./temp/tests_cei_trades/') + os.environ['CPF'] + '/'
        if not os.path.exists(directory):
            os.makedirs(directory)

        crawler_cei = CrawlerCei(headless=True, directory=directory, debug=True)
        trades = crawler_cei.busca_trades(dropExtras=False)
        assert type(trades) is pd.DataFrame
        assert len(trades)
        print(trades.columns)
        assert 'valor' in trades.columns
        assert 'data' in trades.columns
        assert 'ticker' in trades.columns
        assert 'taxas' in trades.columns
        assert 'operacao' in trades.columns
        assert 'aquisicao_via' in trades.columns
        assert 'qtd_ajustada' in trades.columns
        assert 'qtd' in trades.columns
        # Grava arquivo com todos os dados sem remover colunas adicionais para facilitar analise
        with open(directory + "todos_trades.txt", "w") as file:
           file.write(tabulate(trades, headers=trades.columns, showindex=True, tablefmt='psql'))
        
        
        
        
    @unittest.skipUnless('SENHA_CEI' in os.environ, "sem configuracao de acesso CEI")
    def test_busca_carteira(self):
        # Permite separar os arquivos de testes por CPF
        directory = os.getenv('DIR_TESTES_CEI','./temp/tests_cei_carteira/') + os.environ['CPF'] + '/'
        if not os.path.exists(directory):
            os.makedirs(directory)

        crawler_cei = CrawlerCei(headless=True, directory=directory, debug=True)
        carteira = crawler_cei.busca_carteira(datetime.date(2020,12,31))
        verifica_carteira(carteira, directory)
        

    @unittest.skipUnless(os.path.exists(HTML_CARTEIRA), "sem arquivo de teste de carteira")
    def test_busca_carteira_html(self):
        # Permite separar os arquivos de testes por CPF
        directory = os.getenv('DIR_TESTES_CEI','./temp/tests_cei_carteira/') + os.environ['CPF'] + '/'
        if not os.path.exists(directory):
            os.makedirs(directory)

        crawler_cei = CrawlerCei(headless=True, directory=directory, debug=True)
        with open(HTML_CARTEIRA) as file:
            carteira = crawler_cei.converte_html_carteira(file.read())
            self.verifica_carteira(carteira, directory)
        
        


    # Verifica se dados da carteira foram tratados e estao com estrutura esperada
    def verifica_carteira(self, carteira, directory):
        assert type(carteira) is pd.DataFrame
        assert len(carteira)
        assert 'valor' in carteira.columns
        assert 'empresa' in carteira.columns
        assert 'ticker' in carteira.columns
        assert 'qtd' in carteira.columns
        assert 'agente' in carteira.columns
        assert 'conta' in carteira.columns
        assert 'carteira' in carteira.columns
        with open(directory + "carteira.txt", "w") as file:
           file.write(tabulate(carteira, headers=carteira.columns, showindex=True, tablefmt='psql'))
        
        
        
        
        
        