# ir - Projeto de calculo de Imposto de Renda em operacoes na bovespa automaticamente (Work in progress)

## o que ele se propoe a fazer
 - Automaticamente busca todos as suas operacoes na bolsa no site do canal eletronico do investidor (CEI) (https://cei.b3.com.br/)
 - Apos buscar os trades no CEI, salva tudo em um arquivo csv no dropbox
 - Todo dia 5 de cada mes executa e calcula (**automaticamente**):
    - Preco medio de compra
    - Preco medio de venda
    - Lucro/Prejuizo no mes
    - IR a pagar, ja considerando o possivel prejuizo acumulado
    - Tabela com a custodia atual para conferencia
    - Envia email com todas as informacoes para voce pagar o imposto
 - A ideia é ser TUDO automatico, mas ainda ter a opcao de voce manualmente ter controle de tudo via um arquivo csv.
    
   
## disclaimer
 - Aceito PRs :-)   Eu fiz o software pensando em automatizar exatamente como eu fazia as coisas manualmente
 - Nao funciona com daytrade


# TODO list
    - envio de emails com html/pdf
    - geracao de darf? 
    - mirror github
   
# techstack
    - python
    - selenium
    - gitlab ci
    - beautifulsoap
    - pandas
    
    
# tags
canal eletronico do investidor, CEI, selenium, bovespa, IRPF, IR, imposto de renda, finance, yahoo finance, acao, fii, 
etf, python, crawler, webscraping, calculadora ir