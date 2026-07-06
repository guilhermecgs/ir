# Skill de extração de movimentações via printscreen — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a project-level Claude Code skill that turns printscreens of brokerage/portfolio-site movement tables into validated, deduplicated, ready-to-paste lines for `export_operacoes.txt`, without ever writing the file automatically.

**Architecture:** A pure-Python module (`src/movimentacoes_print.py`) holds all deterministic logic — format validation, duplicate-key computation, classification, txt-line formatting — fully unit tested. A thin CLI entrypoint in the same file lets the skill invoke it via `python3 -m src.movimentacoes_print <candidatos.json> <export_operacoes.txt>` and get back a JSON classification. A `SKILL.md` under `.claude/skills/extrai-movimentacoes-print/` orchestrates the non-deterministic part (reading images via Claude's vision, building the candidates JSON) and calls the deterministic CLI for validation/dedup, then renders the two-block output. No network calls to third-party sites, no login, no CPF gate, no CI wiring.

**Tech Stack:** Python 3, pytest (existing project test stack), stdlib only (`csv`, `re`, `datetime`, `json`) — no new dependencies.

## Global Constraints

- Target line format for `export_operacoes.txt` (tab-separated, no header, 7 columns): `ticker\toperacao\tqtd\tdata\tpreco\ttaxas\taquisicao_via` (from spec, matches `src/stuff.py::colunas_obrigatorias`).
- `operacao` must be literally `Compra` or `Venda` — anything else breaks `calculate_add` in `src/stuff.py`.
- `data` format: `DD/MM/AAAA` or `DD/MM/AA`, parsed with day-first semantics (matches rest of codebase).
- `taxas` is always written as `0.000` (project-wide convention — no fee calculation anywhere in this codebase).
- `aquisicao_via` for lines produced by this skill is always `HomeBroker` (same convention as `src/crawler_cei.py` and `src/importador_negociacao_b3.py` — real broker trades, just read via screenshot instead of automated scraping).
- Ticker format: `^[A-Z]{4}\d{1,2}$` (4 uppercase letters + 1-2 digits).
- The skill never writes to `export_operacoes.txt` — output is always presented for manual copy-paste.
- No scraping, no login automation, no CPF gate, no CI pipeline changes — this feature is 100% local and manual (explicitly out of scope per spec).

---

### Task 1: Format validation primitives

**Files:**
- Create: `src/movimentacoes_print.py`
- Test: `tests/test_movimentacoes_print.py`

**Interfaces:**
- Consumes: nothing (first task).
- Produces:
  - `parse_data(data_str: str) -> datetime.date | None`
  - `validar_formato(registro: dict) -> tuple[bool, str | None]` — `registro` has keys `ticker`, `tipo`, `qtd`, `data`, `preco`, and optionally `valor`. Returns `(True, None)` if all format checks pass, else `(False, "<motivo>")`.
  - `TICKER_REGEX: re.Pattern`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_movimentacoes_print.py`:

```python
import datetime

from src.movimentacoes_print import parse_data, validar_formato


class TestParseData:

    def test_parse_data_com_ano_com_4_digitos(self):
        assert parse_data('02/06/2025') == datetime.date(2025, 6, 2)

    def test_parse_data_com_ano_com_2_digitos(self):
        assert parse_data('02/06/25') == datetime.date(2025, 6, 2)

    def test_parse_data_invalida_retorna_none(self):
        assert parse_data('31/13/2025') is None
        assert parse_data('nao e uma data') is None


class TestValidarFormato:

    def registro_valido(self, **overrides):
        base = {'ticker': 'ITRI11', 'tipo': 'Venda', 'qtd': 550, 'data': '02/06/2025', 'preco': 81.2, 'valor': 44660}
        base.update(overrides)
        return base

    def test_registro_valido_passa(self):
        ok, motivo = validar_formato(self.registro_valido())
        assert ok is True
        assert motivo is None

    def test_ticker_fora_do_padrao_falha(self):
        ok, motivo = validar_formato(self.registro_valido(ticker='itri11'))
        assert ok is False
        assert 'ticker' in motivo

    def test_data_invalida_falha(self):
        ok, motivo = validar_formato(self.registro_valido(data='31/13/2025'))
        assert ok is False
        assert 'data' in motivo

    def test_qtd_zero_falha(self):
        ok, motivo = validar_formato(self.registro_valido(qtd=0))
        assert ok is False
        assert 'qtd' in motivo

    def test_qtd_nao_numerica_falha(self):
        ok, motivo = validar_formato(self.registro_valido(qtd='abc'))
        assert ok is False
        assert 'qtd' in motivo

    def test_preco_negativo_falha(self):
        ok, motivo = validar_formato(self.registro_valido(preco=-1))
        assert ok is False
        assert 'preco' in motivo

    def test_valor_incompativel_com_qtd_vezes_preco_falha(self):
        ok, motivo = validar_formato(self.registro_valido(valor=999999))
        assert ok is False
        assert 'valor' in motivo

    def test_valor_ausente_nao_falha(self):
        registro = self.registro_valido()
        del registro['valor']
        ok, motivo = validar_formato(registro)
        assert ok is True
        assert motivo is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_movimentacoes_print.py -v`
Expected: `ModuleNotFoundError: No module named 'src.movimentacoes_print'` (or collection error) — the module doesn't exist yet.

- [ ] **Step 3: Write minimal implementation**

Create `src/movimentacoes_print.py`:

```python
import datetime
import re

TICKER_REGEX = re.compile(r'^[A-Z]{4}\d{1,2}$')
TIPOS_PADRAO = {'Compra', 'Venda'}
TOLERANCIA_VALOR = 0.01  # 1% de tolerancia entre valor informado e qtd*preco


def parse_data(data_str):
    if not isinstance(data_str, str):
        return None
    for fmt in ('%d/%m/%Y', '%d/%m/%y'):
        try:
            return datetime.datetime.strptime(data_str, fmt).date()
        except ValueError:
            continue
    return None


def validar_formato(registro):
    ticker = registro.get('ticker', '')
    if not TICKER_REGEX.match(ticker):
        return False, f'ticker fora do padrao esperado (4 letras + 1-2 digitos): {ticker!r}'

    data = parse_data(registro.get('data'))
    if data is None:
        return False, f'data invalida: {registro.get("data")!r}'

    try:
        qtd = float(registro.get('qtd'))
    except (TypeError, ValueError):
        return False, f'qtd invalida (nao numerica): {registro.get("qtd")!r}'
    if qtd <= 0:
        return False, f'qtd deve ser maior que zero: {qtd}'

    try:
        preco = float(registro.get('preco'))
    except (TypeError, ValueError):
        return False, f'preco invalido (nao numerico): {registro.get("preco")!r}'
    if preco <= 0:
        return False, f'preco deve ser maior que zero: {preco}'

    if 'valor' in registro and registro['valor'] is not None:
        try:
            valor = float(registro['valor'])
        except (TypeError, ValueError):
            return False, f'valor invalido (nao numerico): {registro.get("valor")!r}'
        esperado = qtd * preco
        if esperado > 0 and abs(valor - esperado) / esperado > TOLERANCIA_VALOR:
            return False, f'valor informado ({valor}) nao bate com qtd*preco ({esperado:.2f})'

    return True, None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_movimentacoes_print.py -v`
Expected: all `TestParseData` and `TestValidarFormato` tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/movimentacoes_print.py tests/test_movimentacoes_print.py
git commit -m "feat: adiciona validacao de formato para movimentacoes extraidas de print"
```

---

### Task 2: Duplicate key computation and existing-file parsing

**Files:**
- Modify: `src/movimentacoes_print.py`
- Modify: `tests/test_movimentacoes_print.py`

**Interfaces:**
- Consumes: `parse_data` from Task 1.
- Produces:
  - `chave_duplicidade(ticker: str, operacao: str, qtd, data_str: str, preco) -> tuple` — normalized hashable key.
  - `parse_arquivo_operacoes(caminho: str) -> list[tuple]` — reads a tab-separated operations file and returns one `chave_duplicidade`-shaped tuple per line.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_movimentacoes_print.py`:

```python
from src.movimentacoes_print import chave_duplicidade, parse_arquivo_operacoes


class TestChaveDuplicidade:

    def test_mesma_movimentacao_gera_mesma_chave_mesmo_com_formatacao_diferente(self):
        chave1 = chave_duplicidade('ITRI11', 'Venda', 550, '02/06/2025', 81.2)
        chave2 = chave_duplicidade('ITRI11', 'Venda', 550.0, '02/06/25', 81.200)
        assert chave1 == chave2

    def test_movimentacoes_diferentes_geram_chaves_diferentes(self):
        chave1 = chave_duplicidade('ITRI11', 'Venda', 550, '02/06/2025', 81.2)
        chave2 = chave_duplicidade('ITRI11', 'Venda', 600, '02/06/2025', 81.2)
        assert chave1 != chave2


class TestParseArquivoOperacoes:

    def test_parse_arquivo_com_linhas_reais(self, tmp_path):
        arquivo = tmp_path / 'export_operacoes.txt'
        arquivo.write_text(
            'ITRI11\tVenda\t550.000\t02/06/25\t81.200\t0.000\tHomeBroker\n'
            'BBAS3\tCompra\t1500.000\t16/05/25\t25.700\t0.000\tHomeBroker\n'
        )

        chaves = parse_arquivo_operacoes(str(arquivo))

        assert chave_duplicidade('ITRI11', 'Venda', 550, '02/06/25', 81.2) in chaves
        assert chave_duplicidade('BBAS3', 'Compra', 1500, '16/05/25', 25.7) in chaves
        assert len(chaves) == 2

    def test_parse_arquivo_vazio(self, tmp_path):
        arquivo = tmp_path / 'export_operacoes.txt'
        arquivo.write_text('')

        assert parse_arquivo_operacoes(str(arquivo)) == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_movimentacoes_print.py -v`
Expected: `ImportError: cannot import name 'chave_duplicidade'`.

- [ ] **Step 3: Write minimal implementation**

Append to `src/movimentacoes_print.py`:

```python
import csv


def chave_duplicidade(ticker, operacao, qtd, data_str, preco):
    data = parse_data(data_str)
    return (ticker, operacao, round(float(qtd), 3), data, round(float(preco), 3))


def parse_arquivo_operacoes(caminho):
    chaves = []
    with open(caminho, newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) < 5:
                continue
            ticker, operacao, qtd, data_str, preco = row[0], row[1], row[2], row[3], row[4]
            chaves.append(chave_duplicidade(ticker, operacao, qtd, data_str, preco))
    return chaves
```

Move the `import csv` line to the top of the file alongside the existing `import datetime` and `import re`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_movimentacoes_print.py -v`
Expected: all tests PASS, including the two new test classes.

- [ ] **Step 5: Commit**

```bash
git add src/movimentacoes_print.py tests/test_movimentacoes_print.py
git commit -m "feat: adiciona chave de duplicidade e parser do arquivo de operacoes"
```

---

### Task 3: Classification engine and txt-line formatting

**Files:**
- Modify: `src/movimentacoes_print.py`
- Modify: `tests/test_movimentacoes_print.py`

**Interfaces:**
- Consumes: `validar_formato`, `chave_duplicidade` from Tasks 1-2; `TIPOS_PADRAO` from Task 1.
- Produces:
  - `formatar_linha_txt(registro: dict) -> str`
  - `classificar_candidatos(candidatos: list[dict], chaves_existentes: list[tuple]) -> list[dict]` — returns the same candidates, in order, each with three extra keys: `categoria` (`'pronto'` or `'observacao'`), `motivo` (`str | None`, set when `categoria == 'observacao'`), `linha_txt` (`str | None`, set when `categoria == 'pronto'`).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_movimentacoes_print.py`:

```python
from src.movimentacoes_print import formatar_linha_txt, classificar_candidatos


class TestFormatarLinhaTxt:

    def test_formata_linha_igual_ao_arquivo_real(self):
        registro = {'ticker': 'ITRI11', 'tipo': 'Venda', 'qtd': 550, 'data': '02/06/25', 'preco': 81.2}
        assert formatar_linha_txt(registro) == 'ITRI11\tVenda\t550.000\t02/06/25\t81.200\t0.000\tHomeBroker'


class TestClassificarCandidatos:

    def test_candidato_valido_e_novo_fica_pronto(self):
        candidatos = [{'ticker': 'BBAS3', 'tipo': 'Compra', 'qtd': 1500, 'data': '16/05/25', 'preco': 25.7}]

        resultado = classificar_candidatos(candidatos, chaves_existentes=[])

        assert resultado[0]['categoria'] == 'pronto'
        assert resultado[0]['linha_txt'] == 'BBAS3\tCompra\t1500.000\t16/05/25\t25.700\t0.000\tHomeBroker'
        assert resultado[0]['motivo'] is None

    def test_candidato_com_formato_invalido_vira_observacao(self):
        candidatos = [{'ticker': 'invalido', 'tipo': 'Compra', 'qtd': 100, 'data': '16/05/25', 'preco': 10}]

        resultado = classificar_candidatos(candidatos, chaves_existentes=[])

        assert resultado[0]['categoria'] == 'observacao'
        assert 'ticker' in resultado[0]['motivo']
        assert resultado[0]['linha_txt'] is None

    def test_tipo_fora_do_padrao_vira_observacao_com_campos_preservados(self):
        candidatos = [{'ticker': 'BBAS3', 'tipo': 'Desdobramento', 'qtd': 100, 'data': '16/05/25', 'preco': 10}]

        resultado = classificar_candidatos(candidatos, chaves_existentes=[])

        assert resultado[0]['categoria'] == 'observacao'
        assert 'Desdobramento' in resultado[0]['motivo']
        assert resultado[0]['ticker'] == 'BBAS3'
        assert resultado[0]['linha_txt'] is None

    def test_candidato_duplicado_no_arquivo_existente_vira_observacao(self):
        candidatos = [{'ticker': 'ITRI11', 'tipo': 'Venda', 'qtd': 550, 'data': '02/06/25', 'preco': 81.2}]
        chaves_existentes = [chave_duplicidade('ITRI11', 'Venda', 550, '02/06/25', 81.2)]

        resultado = classificar_candidatos(candidatos, chaves_existentes)

        assert resultado[0]['categoria'] == 'observacao'
        assert 'ja existe' in resultado[0]['motivo']

    def test_dois_candidatos_identicos_no_mesmo_lote_segundo_vira_observacao(self):
        candidato = {'ticker': 'BBAS3', 'tipo': 'Compra', 'qtd': 1500, 'data': '16/05/25', 'preco': 25.7}
        candidatos = [dict(candidato), dict(candidato)]

        resultado = classificar_candidatos(candidatos, chaves_existentes=[])

        assert resultado[0]['categoria'] == 'pronto'
        assert resultado[1]['categoria'] == 'observacao'
        assert 'ja existe' in resultado[1]['motivo']
```

Add the needed import at the top of the test file: `from src.movimentacoes_print import chave_duplicidade` is already imported from Task 2 — reuse it in this test class too (no new import line needed since it's in the same file).

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_movimentacoes_print.py -v`
Expected: `ImportError: cannot import name 'formatar_linha_txt'`.

- [ ] **Step 3: Write minimal implementation**

Append to `src/movimentacoes_print.py`:

```python
def formatar_linha_txt(registro):
    return '\t'.join([
        registro['ticker'],
        registro['tipo'],
        f"{float(registro['qtd']):.3f}",
        registro['data'],
        f"{float(registro['preco']):.3f}",
        '0.000',
        'HomeBroker',
    ])


def classificar_candidatos(candidatos, chaves_existentes):
    vistos = set(chaves_existentes)
    resultado = []

    for candidato in candidatos:
        item = dict(candidato)
        item['categoria'] = None
        item['motivo'] = None
        item['linha_txt'] = None

        ok, motivo_formato = validar_formato(candidato)
        if not ok:
            item['categoria'] = 'observacao'
            item['motivo'] = motivo_formato
            resultado.append(item)
            continue

        if candidato['tipo'] not in TIPOS_PADRAO:
            item['categoria'] = 'observacao'
            item['motivo'] = f'tipo fora do padrao compra/venda: {candidato["tipo"]}'
            resultado.append(item)
            continue

        chave = chave_duplicidade(candidato['ticker'], candidato['tipo'], candidato['qtd'], candidato['data'], candidato['preco'])
        if chave in vistos:
            item['categoria'] = 'observacao'
            item['motivo'] = 'ja existe (arquivo atual ou outro print deste lote)'
            resultado.append(item)
            continue

        vistos.add(chave)
        item['categoria'] = 'pronto'
        item['linha_txt'] = formatar_linha_txt(candidato)
        resultado.append(item)

    return resultado
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_movimentacoes_print.py -v`
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/movimentacoes_print.py tests/test_movimentacoes_print.py
git commit -m "feat: adiciona classificacao de candidatos (pronto vs observacao)"
```

---

### Task 4: CLI entrypoint

**Files:**
- Modify: `src/movimentacoes_print.py`
- Modify: `tests/test_movimentacoes_print.py`

**Interfaces:**
- Consumes: `classificar_candidatos`, `parse_arquivo_operacoes` from Tasks 2-3.
- Produces: `executar_classificacao(candidatos_path: str, operacoes_path: str) -> str` (returns a JSON string), plus a `__main__` block that calls it with `sys.argv[1]`/`sys.argv[2]` and prints the result.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_movimentacoes_print.py`:

```python
import json

from src.movimentacoes_print import executar_classificacao


class TestExecutarClassificacao:

    def test_executar_classificacao_le_arquivos_e_retorna_json(self, tmp_path):
        operacoes = tmp_path / 'export_operacoes.txt'
        operacoes.write_text('ITRI11\tVenda\t550.000\t02/06/25\t81.200\t0.000\tHomeBroker\n')

        candidatos_path = tmp_path / 'candidatos.json'
        candidatos_path.write_text(json.dumps([
            {'ticker': 'ITRI11', 'tipo': 'Venda', 'qtd': 550, 'data': '02/06/25', 'preco': 81.2},
            {'ticker': 'BBAS3', 'tipo': 'Compra', 'qtd': 1500, 'data': '16/05/25', 'preco': 25.7},
        ]))

        resultado_json = executar_classificacao(str(candidatos_path), str(operacoes))
        resultado = json.loads(resultado_json)

        assert resultado[0]['categoria'] == 'observacao'
        assert 'ja existe' in resultado[0]['motivo']
        assert resultado[1]['categoria'] == 'pronto'
        assert resultado[1]['linha_txt'] == 'BBAS3\tCompra\t1500.000\t16/05/25\t25.700\t0.000\tHomeBroker'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_movimentacoes_print.py -v`
Expected: `ImportError: cannot import name 'executar_classificacao'`.

- [ ] **Step 3: Write minimal implementation**

Append to `src/movimentacoes_print.py`:

```python
import json
import sys


def executar_classificacao(candidatos_path, operacoes_path):
    with open(candidatos_path, encoding='utf-8') as f:
        candidatos = json.load(f)
    chaves_existentes = parse_arquivo_operacoes(operacoes_path)
    resultado = classificar_candidatos(candidatos, chaves_existentes)
    return json.dumps(resultado, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    print(executar_classificacao(sys.argv[1], sys.argv[2]))
```

Move `import json` and `import sys` to the top of the file with the other imports.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_movimentacoes_print.py -v`
Expected: all tests in the file PASS (run the full file to confirm no regressions: `pytest tests/test_movimentacoes_print.py -v` should show every test from Tasks 1-4 green).

- [ ] **Step 5: Manually verify the CLI works end-to-end**

Run:

```bash
cd /Users/guilhermesilveira/projects/pessoal/ir
mkdir -p /tmp/mp_smoke
printf 'ITRI11\tVenda\t550.000\t02/06/25\t81.200\t0.000\tHomeBroker\n' > /tmp/mp_smoke/export_operacoes.txt
printf '[{"ticker":"BBAS3","tipo":"Compra","qtd":1500,"data":"16/05/25","preco":25.7}]' > /tmp/mp_smoke/candidatos.json
python3 -m src.movimentacoes_print /tmp/mp_smoke/candidatos.json /tmp/mp_smoke/export_operacoes.txt
```

Expected output: a JSON array with one item, `"categoria": "pronto"` and `"linha_txt": "BBAS3\tCompra\t1500.000\t16/05/25\t25.700\t0.000\tHomeBroker"`.

- [ ] **Step 6: Commit**

```bash
git add src/movimentacoes_print.py tests/test_movimentacoes_print.py
git commit -m "feat: adiciona CLI de classificacao de movimentacoes extraidas de print"
```

---

### Task 5: SKILL.md — orchestration instructions

**Files:**
- Create: `.claude/skills/extrai-movimentacoes-print/SKILL.md`

**Interfaces:**
- Consumes: `python3 -m src.movimentacoes_print <candidatos.json> <export_operacoes.txt>` (CLI from Task 4), `download_dropbox_file()` from `src/dropbox_files.py` (existing), `config.DROPBOX_FILE_LOCATION` (existing).
- Produces: the skill itself (no further task consumes this as code — it's the end-user-facing artifact).

- [ ] **Step 1: Confirm the existing Dropbox download entrypoint**

`src/dropbox_files.py` already defines:

```python
OPERATIONS_FILEPATH = 'export_operacoes.txt'

def download_dropbox_file():
    dbx = dropbox.Dropbox(config.DROPBOX_API_KEY)
    dbx.files_download_to_file(OPERATIONS_FILEPATH, config.DROPBOX_FILE_LOCATION)
    ...
```

`download_dropbox_file()` takes no arguments — it reads `config.DROPBOX_API_KEY`/`config.DROPBOX_FILE_LOCATION` internally and writes to the relative path `export_operacoes.txt` (project root, exported as `OPERATIONS_FILEPATH`). Use this exact call and this exact path in Step 3 below.

- [ ] **Step 2: Create the skill directory**

```bash
mkdir -p .claude/skills/extrai-movimentacoes-print
```

- [ ] **Step 3: Write the skill file**

Create `.claude/skills/extrai-movimentacoes-print/SKILL.md`:

```markdown
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

Isso atualiza o arquivo local em `OPERATIONS_FILEPATH` (ver
`src/dropbox_files.py`). Use esse caminho — não uma cópia antiga — nos passos
seguintes.

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
python3 -m src.movimentacoes_print /tmp/candidatos_movimentacoes.json <caminho_do_OPERATIONS_FILEPATH>
```

O caminho do arquivo de operações é o mesmo baixado no passo 1 — confirme o
valor exato de `OPERATIONS_FILEPATH` rodando
`python3 -c "from src.dropbox_files import OPERATIONS_FILEPATH; print(OPERATIONS_FILEPATH)"`
se não souber o caminho de cor.

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
```

- [ ] **Step 4: Verify the skill file end-to-end with a synthetic scenario**

Since there's no real screenshot in this repo to test image-reading against,
verify the deterministic half of the flow manually:

```bash
cd /Users/guilhermesilveira/projects/pessoal/ir
python3 -c "from src.dropbox_files import OPERATIONS_FILEPATH; print(OPERATIONS_FILEPATH)"
```

Confirm this prints a path (don't worry if the Dropbox download itself needs
real credentials to succeed in this environment — that path is already
covered by existing tests in `tests/test_dropbox_files.py`). Then re-run the
Task 4 smoke test commands to confirm the CLI call documented in Step 3 above
uses the exact same module invocation (`python3 -m src.movimentacoes_print`)
and produces the same shape of output described in the SKILL.md.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/extrai-movimentacoes-print/SKILL.md
git commit -m "feat: adiciona skill de extracao de movimentacoes via printscreen"
```

---

### Task 6: README documentation

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: nothing new — documents Tasks 1-5.
- Produces: nothing consumed by other tasks (end of plan).

- [ ] **Step 1: Add a new README section**

Insert a new section right after the existing "## Exemplo de importação manual
de negociações" section (currently ending around the line with "4. Remova os
arquivos da pasta `importar`"), before "## disclaimer":

```markdown
## Extração de movimentações via printscreen (skill)

Alternativa ao CEI/import manual de XLSX: uma skill do Claude Code
(`.claude/skills/extrai-movimentacoes-print/`) lê printscreens do extrato de
movimentações de qualquer site (investidor10, portal da B3, corretora, etc.),
valida o formato, detecta duplicidade contra o arquivo de operações atual, e
apresenta linhas prontas para colar manualmente em `export_operacoes.txt`.

1. Tire printscreen(s) da tela de extrato/movimentações
2. Peça para o Claude Code usar a skill `extrai-movimentacoes-print` passando
   os paths das imagens
3. Copie as linhas do bloco "PRONTO PARA COPIAR" para `export_operacoes.txt`
4. Revise o bloco "OBSERVAÇÕES" — tipos de movimentação fora de compra/venda
   (desdobramento, conversão, subscrição, bonificação) precisam de
   codificação manual, seguindo os exemplos na seção "Exemplos de Ajustes
   manuais" abaixo

A skill nunca escreve no arquivo sozinha — a inserção final é sempre manual.
```

- [ ] **Step 2: Verify the section renders correctly**

Run: `grep -n "Extração de movimentações via printscreen" README.md`
Expected: one match, confirming the section was inserted.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: documenta skill de extracao de movimentacoes via printscreen"
```
