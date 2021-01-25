# ir - Projeto de calculo de Imposto de Renda em operações na bovespa automaticamente

## o que se propõe a fazer
 - Automaticamente busca todos as suas operações na bolsa no site do canal eletrônico do investidor (CEI) (https://cei.b3.com.br/)
 - Funciona com FIIs, ETFs, Acoes e Opções
 - Funciona com qualquer corretora. (Na verdade, nao depende da corretora)
 - Apos buscar os trades no CEI, salva tudo em um arquivo csv no dropbox da sua conta
 - Todo dia 5 de cada mes executa e calcula (**automaticamente**):
    - Preço médio de compra
    - Preço médio de venda
    - Lucro/Prejuízo no mes
    - IR a pagar, ja considerando o possível prejuízo acumulado
    - Tabela com a custodia atual para conferencia
    - Envia email com todas as informações para voce pagar o imposto
 - A ideia é ser TUDO automático, mas ainda ter a opção de voce manualmente ter controle de tudo via um arquivo csv caso algum papel sofra desdobramento ou mude o ticker de negociação

## o que voce vai precisar
 - Uma conta no CEI (https://cei.b3.com.br/)
 - Uma conta no dropbox com API habilitada (https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/)
    - opcional
 - Instalar as dependências necessárias
    - pip install --user -r requirements.txt
 - Configurar as variáveis de ambiente conforme (https://github.com/guilhermecgs/ir/blob/master/tests/test_environment_variables.py)
 - Caso queira pode incluir operações que não estão disponíveis no CEI em um arquivo outras_operacoes.txt (deve seguir o mesmo padrão do arquivo de dados CEI)
    - Essas operações serão combinadas com as operações CEI e salvas em um arquivo combinado.txt
 - Executar os comandos abaixo:
    - ~~python ./ir.py --do check_environment_variables~~
    - python ./ir.py --do busca_trades_e_faz_merge_operacoes
        - busca a lista de operações
    - python ./ir.py --do busca_carteira
        - busca a posição da carteira e salva para verificações posteriores
    - python ./ir.py --do salva_carteira --html nome_do_arquivo
        - processar um html salvo com a posição da carteira sem fazer o login no servidor CEI
        - lembrar que o site CEI é dinâmico, então só é possível salvar corretamente via console de desenvolvimento do browser
    - python ./ir.py --do calculo_ir

   
## exemplo do relatório gerado no seu email
https://github.com/guilhermecgs/ir/blob/master/exemplo_relatorio_automatico.pdf

## Exemplo de variáveis de ambiente:
 - apesar do teste de variáveis obrigar algumas variáveis, algumas podem ser eliminadas para pular algumas funções.


 - **DROPBOX_API_KEY**:jOznaw_xxxxxxxxxxxxxxxxxxxxtkw9ox_a9I_8-_aU2xw1xxxxxxxxxxKWek69Z
    - caso essa variavel não seja definida não vai fazer envio para Dropbox
 - **DROPBOX_FILE_LOCATION**:/Finance/GCGS/export_operacoes_gcgs.txt
    - necessário caso DROPBOX_API_KEY tenha sido definido
 - **SEND_TO**:emaildestinatario@gmail.com
    - destinatário para envio de email
    - caso não seja definido não vai enviar email
 - **SMTP_FROM**:emailremetente@gmail.com
 - **SMTP_HOST**:smtp.gmail.com
    - Não precisa ser definido pois tem default como gmail
 - **SMTP_PORT**:465
    - Não precisa ser definido pois tem default 465 (SMTP+TLS)
 - **SMTP_USER**:emailremetente@gmail.com
 - **SMTP_PASSWORD**:minha_senha_gmail
 - **CPF**:00098765434
 - **SENHA_CEI**:minha_senha_cei
 - **IGNORA_AGENTES_OPERACOES**
    - Lista com números dos agentes/corretoras a ignorar operações, separados por hífen ex: 3-308-4015
    - Não vai buscar no sistema CEI operações dos agentes/corretoras com os números especificados
    - Util quando tem conta em mais de uma corretora mas opera somente em uma, pois deixa o processo bem mais rápido
 - **WORK_DIR**:./00098765434/
    - Caso seja definido permite armazenar arquivos em um diretório especifico
    - Recomendado para quem for utilizar para mais de uma pessoa, criando um diretório para cada CPF
 - **RELATORIOS_TOTAIS**
    - define as totalizações que serão calculadas para os ativos 
    - cada conjunto de totalização separado por hífen **-**
    - cada conjunto de totalização deve ter o nome da coluna a totalizar ou o
    nome da coluna e totalizar e o nome da coluna default caso não tenha
    valor separado por dois pontos **:**
    - ex. **tipo-carteira:tipo**
 - **RELATORIOS_COLUNAS_EXTRAS**
    - define colunas adicionais que devem ser incluidas no relatório padrão 
    - ex. **nome-carteira:Carteira-setor:Setor**
 - **RELATORIOS_COLUNAS_IRPF**
    - define colunas adicionais que devem ser incluidas no relatório gerado na data de referência 31/12
    - ex. **cnpj-nome-cnpj_adm-nome_adm-ri_url**
 - **CUSTODIA_INCLUI_ZERO**
    - **1** - define que deve apresentar os valores já zerados por venda também na lista de custódia      

# Arquivos gerenciados pelo sistema
  - **export_operacoes.txt**
    - dados obtidos do sistema CEI das operações efetuadas

# Arquivos de dados de operações adicionais (opcionais e carregados na sequencia que estão listados)
  - **outras_operacoes.txt**
  - **custos.txt**
  - **ofertas_publicas.txt**
  - **subscricoes.txt**
  - devem seguir o mesmo formato do **export_operacoes.txt**
  - os arquivos com nomes diferentes servem para facilitar a organização do usuario
  - é possível distribuir custos entre diversas ações automaticamente utilizando **@SPLIT** como código do ativo/ticker
  - é possível colocar esses arquivos em diretórios AAAA (ano) caso queira separar 

# Arquivos de dados adicionais que podem ser criados pelo usuário (opcionais)
  - **notas-corretagem.txt**
    - Deve conter os dados das notas de corretagem caso deseje verificar os
      valores processados, quando os dados estão corretos a diferença para notas de corretagem fica zerada
    - caso não seja criado vai ser indicado que existe uma diferença entre o processamento e as notas de corretagem
    - A utilização desse arquivo permite detectar erros de digitação, principalmente ao utilizar os custos e taxas
    - formato "CSV" (separado por TAB) com as colunas : DATA CORRETORA VALOR
  - **conversoes.txt**
    - deve conter dados sobre as conversões de código do ativo que ocorreram
    - formato "CSV" (separado por TAB) com as colunas : TICKER_COMPRA DATA_COMPRA TICKER_NOVO DATA_CONVERSAO
    - ex. VGIP13 10/12/2020 VGIP11 20/01/2021
  - **ativos-meus-dados.yaml**
    - contendo dados adicionais sobre os ativos, chave deve ser o código do ativo e as entradas parametros adicionais 
    - **cnpj**, **nome** do ativo são incluídos no relatório ao executar com data de referencia **31/12/AAAA**
    - **carteira** permite gerar uma totalização de ativos por carteiras
    - **tipo** permite definir um tipo para o ativo independente das buscas externas
        - ex para ETFs que são classificados como ações
```yaml

# Exemplo ativos-meus-dados.yaml

ACME3:
   - nome: Empresa Papa Leguas
   - cnpj: XXX.XXX.XXX/XXXX-XX
   - carteira: dividendos

TABA11:
   - nome: Organizações Tabajara
   - cnpj: XXX.XXX.XXX/XXXX-XX
   - carteira: longo_prazo
```

# Arquivos auxiliares adicionais/opcionais
  - **relatorio_html_head.inc.html**
    - conteúdo a ser incluido no elemento head do relatório html gerado
  - **relatorio_html_body_start.inc.html**
    - conteúdo a ser incluido no inicio do elemento body do relatório html gerado
  - **relatorio_html_body_end.inc.html**
    - conteúdo a ser incluido no final do elemento body do relatório html gerado

# Arquivos gerados pelo sistema
  - **YYYY-MM-DD.txt**
    - relatório do dia em formato texto simples
  - **YYYY-MM-DD.html**
    - relatório do dia em formato html
  - **YYYY-MM-DD-custodia.xlsx**
    - planilha gerada ao utilizar referencia no dia 31/12 
    - facilitador para declaração anual 
  - **diario.txt** ou **YYYY-MM-DD.txt** quando processando data especifica
    - resumo de operações por dia, faz a comparação com as notas de corretagem para identificação de possíveis erros
  - **combinado.txt** ou **YYYY-MM-DD.txt** quando processando dados especifica
    - dados combinados dos arquivos de operações para facilitar analise em caso de erros



## disclaimer
 - Aceito PRs :-)   Eu fiz o software pensando em automatizar exatamente como eu fazia as coisas manualmente
 - Nao funciona com daytrade
 - Desconsidera custos e emolumentos para simplificação do calculo
    - implementação inicial permitindo considerar os custos
    - custos/taxas podem ser colocados nos arquivos adicionais, criando uma operação com quantidade 0, mas deve ser colocado no mesmo dia da operação original
 - Utilizando cachier para reduzir o volume de requisições remotas
    - caso queira atualização total dos valores dos ativos, a melhor maneira é remover o cache do  diretório ~/.cachier
 - o sistema CEI as vezes fica bem lento e é necessário tentar mais de uma vez para baixar os dados
      

# To do list
    - Incluir gratuidade de 20k por mes para acoes
    - Incluir desconto de taxas, emolumentos e dedo duro - http://www.b3.com.br/pt_br/produtos-e-servicos/tarifas/listados-a-vista-e-derivativos/renda-variavel/tarifas-de-acoes-e-fundos-de-investimento/a-vista/
    - Utilizar um framework de log para facilitar o acompanhamento da execução
    - Saídas para facilitar a declaração anual
    - Separar o tratamento de BDR
    - Ajustar saída html 
        - alinhar números na direita
        - opção de indicar perdas com cor diferente
   
# techstack
- python
- selenium
- gitlab ci
- beautifulsoap
- pandas
- cachier
    
# Legislação / Informações
- **FIP**
    - http://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/fundos-de-investimento-em-participacoes-fip.htm
    - https://www.btgpactualdigital.com/blog/coluna-do-assessor/fundos-de-investimento-em-participacoes-fip
    - **FIP-IE**
        - Lei nº 11.478/07 - http://www.planalto.gov.br/ccivil_03/_ato2007-2010/2007/lei/L11478.htm
        - https://www.vincienergia.com.br/governanca-corporativa/caracteristicas-de-um-fip-em-infraestrutura/

    
# tags
canal eletronico do investidor, CEI, selenium, bovespa, IRPF, IR, imposto de renda, finance, yahoo finance, acao, fii, 
etf, python, crawler, webscraping, calculadora ir
