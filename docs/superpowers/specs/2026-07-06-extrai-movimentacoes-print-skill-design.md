# Skill: extração de movimentações via printscreen (investidor10)

Data: 2026-07-06
Status: aguardando revisão do usuário

## Contexto

O projeto `ir` automatiza cálculo de IR sobre operações na bolsa. Historicamente,
buscava negociações via scraping do CEI (`src/crawler_cei.py`), site hoje
substituído pelo novo portal `investidor.b3.com.br`. A busca automática está
atualmente desativada no pipeline (`.gitlab-ci.yml`, linha comentada).

Foi cogitada uma nova integração automática via scraping do site
`investidor10.com.br` (agregador de carteira, não o portal oficial da B3),
usando sessão de cookie (login tem reCAPTCHA invisible, o que impede login
automatizado em pipeline). Essa abordagem foi **descartada** pelo usuário em
favor de um fluxo manual, mais simples e sem dependência de sessão/cookie
expirando:

O usuário navega manualmente no site (qualquer site — investidor10, portal B3,
corretora, etc.), tira printscreen da tela mostrando as movimentações, e usa
uma skill do Claude Code para extrair, validar e checar duplicidade dessas
movimentações antes de inserir manualmente no arquivo de operações.

Não há CPF-gate nem execução em pipeline/CI — esse fluxo é 100% local,
disparado sob demanda pelo próprio usuário. Não há scraping automatizado,
sessão de cookie, nem chamada de rede a sites de terceiros nesta feature.

## Objetivo

Criar uma skill de projeto (`.claude/skills/extrai-movimentacoes-print/`,
dentro do repositório — não a nível de usuário) que:

1. Recebe um ou mais paths de imagem (printscreens) já salvos localmente.
2. Faz download da cópia canônica do arquivo de operações no Dropbox
   (reaproveitando `src/dropbox_files.py::download_dropbox_file` e
   `config.DROPBOX_FILE_LOCATION`/`config.DROPBOX_API_KEY`, já configurados
   no `.env` local do usuário).
3. Extrai as movimentações visíveis em cada print (ticker, tipo de
   movimentação, quantidade, data, preço, valor total, fonte se visível).
4. Valida o formato de cada linha extraída.
5. Detecta duplicidade — contra o arquivo baixado do Dropbox e entre os
   próprios prints do lote.
6. Apresenta a saída em dois blocos: linhas prontas para copiar (formato
   exato do arquivo de operações) e uma lista de observações (tipos fora do
   padrão compra/venda, falhas de validação, duplicatas encontradas).

A inserção final no arquivo `export_operacoes.txt` continua manual — a skill
nunca escreve no arquivo diretamente.

## Formato alvo (referência)

Arquivo de operações (`export_operacoes.txt`, lido por
`src/stuff.py::get_operations`) é texto separado por tab, sem cabeçalho,
7 colunas nesta ordem exata:

```
ticker	operacao	qtd	data	preco	taxas	aquisicao_via
```

Exemplo real (linha existente no arquivo):

```
ITRI11	Venda	550.000	02/06/25	81.200	0.000	HomeBroker
```

- `operacao`: apenas `Compra` ou `Venda` (literal — qualquer outro valor
  quebra `calculate_add` em `stuff.py`, que assume `== 'Compra'` para tratar
  o resto como venda).
- `data`: `DD/MM/AA` (ou `DD/MM/AAAA`, ambos parseáveis com `dayfirst=True`).
- `taxas`: a skill sempre preenche `0.000` (mesmo padrão do restante do
  código, que não calcula taxas — ver disclaimer do README).
- `aquisicao_via`: valor livre usado só para rastrear origem (não afeta
  cálculo, mas afeta o corte de data em `merge_operacoes`, que só olha linhas
  com `aquisicao_via == 'HomeBroker'`). Para as linhas geradas por esta skill,
  usar `HomeBroker` — são negociações reais de corretora, só lidas via print
  em vez de scraping automático, mesma convenção do CEI/import xlsx.

## Passo a passo da skill

### 1. Sincronizar cópia canônica

Antes de checar duplicidade, a skill roda o download do Dropbox (mesma
chamada usada em `do_calculo_ir`/`do_busca_trades_e_faz_merge_operacoes` em
`ir.py`) para garantir que a comparação de duplicidade usa o estado mais
recente conhecido, não uma cópia local potencialmente desatualizada.

### 2. Extração por print

Para cada imagem: leitura via Read (visão do modelo) para extrair uma lista
de registros brutos com os campos visíveis na tela — ticker, tipo (rótulo
literal como aparece: `Compra`, `Venda`, `Desdobramento`, `Bonificação`,
`Subscrição`, `Conversão` etc.), quantidade, data, preço, valor total, e
fonte/observação se o site mostrar (ex: "B3", "Manual", "Evento").

Cada print pode conter várias linhas (tabela de extrato inteira).
Múltiplos prints no mesmo lote são aceitos e processados juntos.

### 3. Validação de formato

Por linha extraída:
- `data` precisa parsear como data válida.
- `qtd` e `preco` precisam ser numéricos e maiores que zero.
- `ticker` precisa casar com o padrão `^[A-Z]{4}\d{1,2}$` (4 letras + 1-2
  dígitos — cobre ações, FIIs, ETFs, BDRs listados na B3).

Linha que falha qualquer checagem não vai para "pronto para copiar" — vira
observação, com o motivo da falha e os campos brutos como foram lidos.

### 4. Separação por tipo de movimentação

- `tipo` em `{Compra, Venda}` → candidata a "pronto para copiar".
- Qualquer outro tipo (desdobramento, conversão, subscrição, bonificação,
  eventos em geral) → vai direto para observações, com os campos brutos.
  Esses tipos exigem codificação manual específica (o README já documenta
  convenções, ex: subscrição vira uma linha de compra sintética,
  desdobramento ajusta ticker/quantidade) — a skill não tenta adivinhar essa
  codificação, só relata o que leu.

### 5. Detecção de duplicidade

Uma linha candidata (`Compra`/`Venda` validada) é considerada duplicata e
movida para observações (com nota "já existe") se bater exatamente em
`ticker + operacao + qtd + data + preco` contra:
- alguma linha já presente no arquivo baixado do Dropbox, ou
- outra linha candidata do mesmo lote (evita contar duas vezes a mesma
  movimentação capturada em dois prints sobrepostos).

Essa comparação roda via um script Python pequeno e determinístico (não
apenas inferência do modelo), para garantir confiabilidade. O script fica
junto da skill (ex: `.claude/skills/extrai-movimentacoes-print/check_duplicates.py`).

### 6. Saída

Dois blocos de texto, sempre nesta ordem:

**PRONTO PARA COPIAR** — uma linha por movimentação validada e não-duplicada,
exatamente no formato tab-separated do arquivo de operações, pronta para colar
manualmente em `export_operacoes.txt`.

**OBSERVAÇÕES** — lista com: tipos de movimentação fora de compra/venda
(campos brutos), falhas de validação (com motivo), duplicatas detectadas
(com onde foi encontrado o match).

A skill nunca escreve em `export_operacoes.txt` — a inserção final é sempre
manual, pelo usuário.

## Fora de escopo (explicitamente descartado)

- Scraping automatizado do investidor10.com.br ou qualquer outro site.
- Login automatizado / gestão de sessão ou cookie.
- Gate de CPF único usuário — não se aplica, fluxo é local e manual.
- Execução via pipeline/CI.
- Checagem de custódia (comparar posição calculada vs. site) — não faz parte
  deste fluxo baseado em print.

## Testes

- Fixtures de imagem (ou JSON simulando a extração) cobrindo: linha
  compra/venda válida, linha com tipo fora do padrão, linha com campo
  inválido (data quebrada, ticker fora do padrão), duplicata exata contra
  arquivo existente, duplicata entre dois prints do mesmo lote.
- Teste do script de detecção de duplicidade isolado (input: lista de
  candidatos + conteúdo do txt; output: quais são duplicata).

## Documentação

- README ganha uma seção curta descrevendo a skill, como invocá-la (paths de
  imagem como argumento) e o fluxo esperado (print → skill → copiar manual
  pro `export_operacoes.txt`).
