import os
import time
import datetime
import re
import pandas as pd
from tabulate import tabulate
from bs4 import BeautifulSoup
from bs4.element import Comment

from selenium import webdriver
import chromedriver_binary  # do not remove
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.driver_selenium import ChromeDriver


class AnyEc:
    """ Use with WebDriverWait to combine expected_conditions
        in an OR.
    """

    def __init__(self, *args):
        self.ecs = args

    def __call__(self, driver):
        for fn in self.ecs:
            try:
                if fn(driver): return True
            except:
                pass


class CrawlerCei():

    def __init__(self, headless=False, directory='./temp/', debug=False):
        self.BASE_URL = 'https://ceiapp.b3.com.br/CEI_Responsivo/'
        self.driver = ChromeDriver()
        self.directory = directory
        self.debug = debug
        self.__colunas_df_cei = ['Data do Negócio', 'Compra/Venda', 'Mercado', 'Prazo/Vencimento', 'Código Negociação',
               'Especificação do Ativo', 'Quantidade', 'Preço (R$)', 'Valor Total(R$)', 'Fator de Cotação']
        self.__colunas_df_carteira = ['Empresa', 'Tipo', 'ticker', 'isin', 'Preço (R$)',
               'Quantidade', 'Fator de Cotação' 'Valor Total(R$)']
        self.id_tabela_negociacao_ativos = 'ctl00_ContentPlaceHolder1_rptAgenteBolsa_ctl00_rptContaBolsa_ctl00_pnAtivosNegociados'
        self.id_mensagem_de_aviso = 'CEIMessageDIV'
        self.id_selecao_corretoras = 'ctl00_ContentPlaceHolder1_ddlAgentes'
        self.id_btn_consultar = 'ctl00_ContentPlaceHolder1_btnConsultar'
        self.id_selecao_data = 'ctl00_ContentPlaceHolder1_txtData'
        self.agentes_ignorar = {}
        if 'IGNORA_AGENTES_OPERACOES' in os.environ:
            self.agentes_ignorar = set(os.environ['IGNORA_AGENTES_OPERACOES'].split("-"))
        

    def busca_trades(self, dropExtras=True):
        try:
            print("Buscando operações CEI para " + os.environ['CPF'])
            if (os.getenv("SENHA_CEI","") == ""):
                raise Exception("Senha CEI não está definida")
            self.driver.get(self.BASE_URL)
            self.__login()
            df = self.__abre_consulta_trades()
            try:
                return self.__converte_dataframe_para_formato_padrao(df, dropExtras)
            except Exception as ex:
                if self.debug:
                    print("*** Erro buscando operações")
                    print(df)
                raise ex
        except Exception as ex:
            self.__save_screenshot('erro_busca_trades-' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '.png', force_save=True)
            raise ex
        finally:
            self.driver.quit()

    def busca_carteira(self, data):
        try:
            print("Buscando carteira CEI para " + os.environ['CPF'] + " " + str(data))
            if (os.getenv("SENHA_CEI","") == ""):
                raise Exception("Senha CEI não está definida")
            self.driver.get(self.BASE_URL)
            self.__login()
            df = self.__abre_consulta_carteira(data)
            return df
        except Exception as ex:
            self.__save_screenshot('erro_busca_carteira-' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '.png', force_save=True)
            raise ex
        finally:
            self.driver.quit()

    def converte_html_carteira(self, html):
        try:
            df = self.__converte_custodia_html_para_dataframe(html, 0, 'Todos')
            return df
        except Exception as ex:
            raise ex

    def __save_screenshot(self, name, force_save=False):
        if self.debug or force_save:
            self.driver.save_screenshot(self.directory + name)
    
    def __login(self):
        self.__save_screenshot(r'01-inicio.png')
        
        txt_login = self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_txtLogin')
        txt_login.clear()
        txt_login.send_keys(os.environ['CPF'])

        time.sleep(3.0)
        txt_senha = self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_txtSenha')
        txt_senha.clear()
        txt_senha.send_keys(os.environ['SENHA_CEI'])
        time.sleep(3.0)

        self.__save_screenshot(r'02-dados-login.png')

        btn_logar = self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_btnLogar')
        btn_logar.click()

        try:
            WebDriverWait(self.driver, 60).until(EC.visibility_of_element_located((By.ID, 'objGrafPosiInv')))
        except Exception as ex:
            self.__save_screenshot(r'03-erro-login.png')
            raise Exception('Nao foi possivel logar no CEI. Possivelmente usuario/senha errada ou indisponibilidade do site') from ex

        self.__save_screenshot(r'03-pos-login.png')

    def consultar_click(self, driver):
        btn_consultar = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, self.id_btn_consultar)))
        btn_consultar.click();

    def exists_and_not_disabled(self, id):
        def until_fn(driver):
            try:
                driver.find_element_by_id(id)
            except NoSuchElementException:
                return False
            return driver.find_element_by_id(id).get_attribute("disabled") is None

        return until_fn

    def __abre_consulta_trades(self):

        dfs_to_concat = []

        self.driver.get(self.BASE_URL + 'negociacao-de-ativos.aspx')
        self.__save_screenshot(r'04-negociacao-ativos.png')

        from selenium.webdriver.support.select import Select
        ddlAgentes = Select(self.driver.find_element_by_id(self.id_selecao_corretoras))

        def __busca_trades_de_uma_corretora(i, nomeAgente):
            print("Verificando Operações : " + str(i) + " " + nomeAgente)
            # O nome do agente é um número/ código e depois vem o nome
            # Utilizar isso para ignorar alguns agentes, não existe motivo para tentar buscar operações se o usuário não faz operações com o agente...
            #  3 - XP INVESTIMENTOS CCTVM S/A
            numeroAgente = nomeAgente.split(" ")[0]
            if numeroAgente in self.agentes_ignorar:
                print("\tIgnorando agente no download de operações")
                return
                
            self.__save_screenshot(r'05_01-' + str(i) + '.png')
            ddlAgentes = Select(self.driver.find_element_by_id(self.id_selecao_corretoras))
            ddlAgentes.select_by_index(i)
            time.sleep(10)
            
            self.__save_screenshot(r'05_02-' + str(i) + '.png')
            WebDriverWait(self.driver, 15).until(self.exists_and_not_disabled(self.id_btn_consultar))
            self.consultar_click(self.driver)

            self.__save_screenshot(r'05_03-' + str(i) + '.png')

            try:
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
                    (By.ID, self.id_mensagem_de_aviso)))
            except:
                pass

            self.__save_screenshot(r'05_04-' + str(i) + '.png')

            # checa se existem trades para essa corretora
            aviso = self.driver.find_element_by_id(self.id_mensagem_de_aviso)
            if aviso.text == 'Não foram encontrados resultados para esta pesquisa.\n×':
                self.consultar_click(self.driver)
                try:
                    WebDriverWait(self.driver, 60).until(self.exists_and_not_disabled(self.id_selecao_corretoras))
                    self.__save_screenshot(r'05_05-sem-resultados-' + str(i) + '.png')
                except StaleElementReferenceException as ex:
                    # Pode ignorar já que não teve dados
                    pass
                print("\tNão existem operações")
            else:
                if not self.exists_and_not_disabled(self.id_tabela_negociacao_ativos)(self.driver):
                    self.consultar_click(self.driver)

                WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(
                    (By.ID, self.id_tabela_negociacao_ativos)))

                self.__save_screenshot(r'05_05-' + str(i) + '.png')
                operacoes = self.__converte_trades_para_dataframe(i, nomeAgente)
                print("\tOperações encontradas : " + str(len(operacoes)))
                dfs_to_concat.append(operacoes)
                self.consultar_click(self.driver)
                WebDriverWait(self.driver, 60).until(self.exists_and_not_disabled(self.id_selecao_corretoras))

        # Durante as buscas os elementos se alteram e o selenium nao consegue obter o texto correto, então salva antes
        opcoesAgentes = ddlAgentes.options
        textosAgentes = []
        for i in range(0,len(opcoesAgentes)):
            textosAgentes.append(opcoesAgentes[i].text)
        # Quando tem mais de um a primeira linha é um texto "Selecione"
        if len(opcoesAgentes) == 1:
            __busca_trades_de_uma_corretora(0, textosAgentes[0])
        else:
            for i in range(1, len(opcoesAgentes)):
                __busca_trades_de_uma_corretora(i, textosAgentes[i])

        if len(dfs_to_concat):
            return pd.concat(dfs_to_concat)
        else:
            return pd.DataFrame(columns=self.__colunas_df_cei)

    def __converte_trades_para_dataframe(self, i, nomeAgente):

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        if self.debug:
            with open(self.directory + "trades-" + str(i) + ".html", "w") as file:
                file.write(soup.prettify())

        top_div = soup.find('div', {'id': self.id_tabela_negociacao_ativos})

        table = top_div.find(lambda tag: tag.name == 'table')
        if self.debug:
            with open(self.directory + "trades-" + str(i) + "-tabela.html", "w") as file:
                file.write(table.prettify())

        df = pd.read_html(str(table), decimal=',', thousands='.')[0]
        df['agente'] = df.apply(lambda row: nomeAgente, axis=1)
        
        if self.debug:
            with open(self.directory + "trades-" + str(i) + ".txt", "w") as file:
                file.write(tabulate(df, headers=df.columns, showindex=True, tablefmt='psql'))
        # Remove totais que vem tambem na tabela
        df = df[df['Data do Negócio'].str.match('\\d+/\\d+/\\d+')]
        if self.debug:
            with open(self.directory + "trades-" + str(i) + "-filtro.txt", "w") as file:
                file.write(tabulate(df, headers=df.columns, showindex=True, tablefmt='psql'))
        
        return df


    def __converte_dataframe_para_formato_padrao(self, df, dropExtras):
        df = df.rename(columns={'Código Negociação': 'ticker',
                                'Compra/Venda': 'operacao',
                                'Quantidade': 'qtd',
                                'Data do Negócio': 'data',
                                'Preço (R$)': 'preco',
                                'Valor Total(R$)': 'valor',
                                })

        from src.stuff import calculate_add

        def formata_compra_venda(operacao):
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

        if dropExtras:
            df.drop(columns=['Mercado', 
                         'Prazo/Vencimento', 
                         'Especificação do Ativo',
                         'Fator de Cotação'], 
                         inplace=True)
        return df

    def __abre_consulta_carteira(self, data):

        dfs_to_concat = []

        self.driver.get(self.BASE_URL + 'ConsultarCarteiraAtivos.aspx')
        self.__save_screenshot(r'04-carteira-ativos.png')

        from selenium.webdriver.support.select import Select
        ddlAgentes = Select(self.driver.find_element_by_id(self.id_selecao_corretoras))

        def __busca_ativos_de_uma_corretora(i, nomeAgente):
            print("Verificando Carteira : " + str(i) + " " + nomeAgente)
            
            self.__save_screenshot(r'05_01-' + str(i) + '.png')
            ddlAgentes = Select(self.driver.find_element_by_id(self.id_selecao_corretoras))
            ddlAgentes.select_by_index(i)
            time.sleep(10)
            
            self.__save_screenshot(r'05_02-' + str(i) + '.png')            
            inputData = self.driver.find_element_by_id(self.id_selecao_data)
            inputData.clear()
            inputData.send_keys(data.strftime('%d/%m/%Y'))
            time.sleep(10)
            
            self.__save_screenshot(r'05_03-' + str(i) + '.png')            
            WebDriverWait(self.driver, 15).until(self.exists_and_not_disabled(self.id_btn_consultar))
            self.consultar_click(self.driver)

            self.__save_screenshot(r'05_04-' + str(i) + '.png')

            try:
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
                    (By.ID, self.id_mensagem_de_aviso)))
            except:
                pass

            self.__save_screenshot(r'05_05-' + str(i) + '.png')

            # checa se existem trades para essa corretora
            aviso = self.driver.find_element_by_id(self.id_mensagem_de_aviso)
            if aviso.text == 'Não foram encontrados resultados para esta pesquisa.\n×':
                self.consultar_click(self.driver)
                try:
                    WebDriverWait(self.driver, 60).until(self.exists_and_not_disabled(self.id_selecao_corretoras))
                    self.__save_screenshot(r'05_06-sem-resultados-' + str(i) + '.png')
                except StaleElementReferenceException as ex:
                    # Pode ignorar já que não teve dados
                    pass
            else:
                self.__save_screenshot(r'05_06-' + str(i) + '.png')
                dfs_to_concat.append(self.__converte_custodia_para_dataframe(i, nomeAgente))
                self.consultar_click(self.driver)
                WebDriverWait(self.driver, 60).until(self.exists_and_not_disabled(self.id_selecao_corretoras))

        # Durante as buscas os elementos se alteram e o selenium nao consegue obter o texto correto, então salva antes
        opcoesAgentes = ddlAgentes.options
        textosAgentes = []
        for i in range(0,len(opcoesAgentes)):
            textosAgentes.append(opcoesAgentes[i].text)
        # A primeira opção é Todos e depois tem as corretoras, parece funcionar bem com todas de uma vez
        __busca_ativos_de_uma_corretora(0, textosAgentes[0])
#        if len(opcoesAgentes) == 1:
#            __busca_ativos_de_uma_corretora(0, textosAgentes[0])
#        else:
#            for i in range(1, len(opcoesAgentes)):
#                __busca_ativos_de_uma_corretora(i, textosAgentes[i])

        if len(dfs_to_concat):
            return pd.concat(dfs_to_concat)
        else:
            return pd.DataFrame(columns=self.__colunas_df_carteira)

    def __converte_custodia_para_dataframe(self, i, nomeAgente):
        return self.__converte_custodia_html_para_dataframe(self.driver.page_source, i, nomeAgente)

    # Separação desse metodo facilita nos testes utilizando html local
    def __converte_custodia_html_para_dataframe(self, html_source, i, nomeAgente):

        dfs_to_concat = []
        
        soup = BeautifulSoup(html_source, 'html.parser')
        if self.debug:
            with open(self.directory + "custodia-" + str(i) + ".html", "w") as file:
                file.write(soup.prettify())


        nomeEl = soup.findAll('span',id=re.compile('ctl00_ContentPlaceHolder1_rptAgenteContaMercado_ctl\\d\\d_lblAgenteContas'))
        for el in nomeEl:
            agente = el.text.strip()
            conta = ''
            # ctl00_ContentPlaceHolder1_rptAgenteContaMercado_ctl00_rptContaMercado_ctl00_lblContaPosicao
            nextId = el['id'].replace('lblAgenteContas','rptContaMercado_ctl\\d\\d_lblContaPosicao')
            next = el.find_parent('div').find_next_sibling('div').find(id=re.compile(nextId))
            if next:
                conta = next.text.strip()

            # ctl00_ContentPlaceHolder1_rptAgenteContaMercado_ctl00_rptContaMercado_ctl00_rprCarteira_ctl00_trBodyCarteira
            nextId = el['id'].replace('lblAgenteContas','rptContaMercado_ctl\\d\\d_rprCarteira_ctl\\d\\d_trBodyCarteira')
            nextTables = el.find_parent('div').find_next_sibling('div').findAll(id=re.compile(nextId))
            for next in nextTables:
                # id="ctl00_ContentPlaceHolder1_rptAgenteContaMercado_ctl02_rptContaMercado_ctl00_rprCarteira_ctl00_lblCarteira"
                nextId = next['id'].replace('trBodyCarteira','lblCarteira')
                lbl = next.find(id=re.compile(nextId))
                carteira = ''
                if lbl:
                    carteira = lbl.text.strip()
                table = next.find('table')
                df = pd.read_html(str(table), decimal=',', thousands='.')[0]
                df['agente'] = df.apply(lambda row: agente, axis=1)
                df['conta'] = df.apply(lambda row: conta, axis=1)
                df['carteira'] = df.apply(lambda row: carteira, axis=1)
                if self.debug:
                    with open(self.directory + "custodia-" + str(i) + "-" + str(len(dfs_to_concat)) + ".html", "w") as file:
                        file.write(table.prettify())

                    with open(self.directory + "custodia-" + str(i) + "-" + str(len(dfs_to_concat)) + "-filtro.txt", "w") as file:
                        file.write(tabulate(df, headers=df.columns, showindex=True, tablefmt='psql'))
                dfs_to_concat.append(df)
        df = pd.concat(dfs_to_concat, ignore_index=True)
        # As linhas de total vem com Nan            
        df = df.dropna()
        df = df.rename(columns={'Empresa': 'empresa',
                                'Tipo': 'tipo',
                                'Cód. de Negociação': 'ticker',
                                'Cod.ISIN': 'isin',
                                'Preço (R$)*': 'preco',
                                'Qtde.': 'qtd',
                                'Fator Cotação': 'fator',
                                'Valor (R$)': 'valor',
                                })
        if self.debug:
            with open(self.directory + "custodia-" + str(i) + "-" + str(len(dfs_to_concat)) + "-combinado.txt", "w") as file:
                file.write(tabulate(df, headers=df.columns, showindex=True, tablefmt='psql'))
        
        return df


        