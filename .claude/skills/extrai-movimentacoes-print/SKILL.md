---
name: extrai-movimentacoes-print
description: Extrai movimentacoes de negociacao (compra/venda e outros tipos) a partir de printscreens de sites de corretora/carteira, valida formato, detecta duplicidade contra o arquivo de operacoes atual, e apresenta linhas prontas para colar manualmente em export_operacoes.txt. Use quando o usuario fornecer um ou mais paths de imagem de extrato/movimentacoes e pedir para extrair/conferir essas movimentacoes.
---

# Extrai movimentações via printscreen

Converte printscreens de extrato de movimentações (qualquer site — investidor10,
portal da B3, corretora, etc.) em linhas prontas para colar manualmente no
arquivo de operações do projeto `ir`. Nunca escreve no arquivo sozinha — a
inserção final é sempre manual.

## Quando usar

O usuário fornece um ou mais paths de imagem (printscreens já salvos
localmente) mostrando uma tabela de movimentações e pede para extrair,
conferir ou validar essas movimentações.

## Passo a passo

### 1. Sincronizar a cópia canônica do arquivo de operações

Antes de checar duplicidade, baixe a versão mais recente do arquivo de
operações do Dropbox (mesma função usada pelo resto do projeto):

```bash
python3 -c "from src.dropbox_files import download_dropbox_file; download_dropbox_file()"
```

Isso atualiza o arquivo local em `OPERATIONS_FILEPATH` (`export_operacoes.txt`,
na raiz do projeto — ver `src/dropbox_files.py`). Use esse caminho — não uma
cópia antiga — nos passos seguintes.

### 2. Ler cada printscreen

Para cada imagem fornecida, use a ferramenta de leitura de imagem para
identificar todas as linhas de movimentação visíveis na tabela. Para cada
linha, extraia:

- `ticker` (código de negociação, ex: `ITRI11`, `BBAS3`)
- `tipo` (rótulo literal como aparece na tela: `Compra`, `Venda`,
  `Desdobramento`, `Bonificação`, `Subscrição`, `Conversão`, etc. — não
  traduza nem normalize, use exatamente o que está escrito)
- `qtd` (quantidade, numérico)
- `data` (formato `DD/MM/AAAA` ou `DD/MM/AA`, como aparece na tela)
- `preco` (preço unitário, numérico)
- `valor` (valor total da operação, se visível — numérico; omita a chave se
  não estiver visível)

Um print pode conter várias linhas — extraia todas. Vários prints no mesmo
lote são normais — junte todas as linhas extraídas de todos os prints numa
única lista, na ordem em que aparecem.

Monte essa lista como um array JSON e escreva num arquivo temporário, por
exemplo `/tmp/candidatos_movimentacoes.json`:

```json
[
  {"ticker": "BBAS3", "tipo": "Compra", "qtd": 1500, "data": "16/05/2025", "preco": 25.70, "valor": 38550},
  {"ticker": "ITRI11", "tipo": "Desdobramento", "qtd": 100, "data": "20/05/2025", "preco": 0, "valor": 0}
]
```

### 3. Rodar a classificação determinística

```bash
python3 -m src.movimentacoes_print /tmp/candidatos_movimentacoes.json export_operacoes.txt
```

O segundo argumento é o mesmo arquivo baixado no passo 1 (`OPERATIONS_FILEPATH`,
`export_operacoes.txt` na raiz do projeto). Se não tiver certeza do caminho,
confirme com:

```bash
python3 -c "from src.dropbox_files import OPERATIONS_FILEPATH; print(OPERATIONS_FILEPATH)"
```

A saída é um JSON com um item por candidato, cada um com:
- `categoria`: `"pronto"` ou `"observacao"`
- `linha_txt`: a linha formatada (só quando `categoria == "pronto"`)
- `motivo`: por que caiu em observação (só quando `categoria == "observacao"`)

### 4. Apresentar o resultado ao usuário em dois blocos

Nunca escreva no arquivo de operações. Apresente sempre neste formato:

```
## PRONTO PARA COPIAR

<uma linha por item com categoria "pronto", usando o valor de linha_txt,
 em bloco de código para facilitar copiar>

## OBSERVAÇÕES

- <ticker> (<tipo>, <data>): <motivo>
- ... (uma linha por item com categoria "observacao")
```

Se não houver nenhum item em "pronto", diga isso explicitamente (não omita a
seção). Se não houver nenhuma observação, também diga isso explicitamente.

## Fora de escopo

Não faça login em nenhum site, não acesse a internet para buscar dados, não
escreva em `export_operacoes.txt`. Esta skill só processa imagens já
fornecidas pelo usuário e o arquivo de operações já sincronizado do Dropbox.
