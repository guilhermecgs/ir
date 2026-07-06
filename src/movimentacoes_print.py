import csv
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
        return False, 'ticker fora do padrao esperado (4 letras + 1-2 digitos): {!r}'.format(ticker)

    data = parse_data(registro.get('data'))
    if data is None:
        return False, 'data invalida: {!r}'.format(registro.get('data'))

    try:
        qtd = float(registro.get('qtd'))
    except (TypeError, ValueError):
        return False, 'qtd invalida (nao numerica): {!r}'.format(registro.get('qtd'))
    if qtd <= 0:
        return False, 'qtd deve ser maior que zero: {}'.format(qtd)

    try:
        preco = float(registro.get('preco'))
    except (TypeError, ValueError):
        return False, 'preco invalido (nao numerico): {!r}'.format(registro.get('preco'))
    if preco <= 0:
        return False, 'preco deve ser maior que zero: {}'.format(preco)

    if 'valor' in registro and registro['valor'] is not None:
        try:
            valor = float(registro['valor'])
        except (TypeError, ValueError):
            return False, 'valor invalido (nao numerico): {!r}'.format(registro.get('valor'))
        esperado = qtd * preco
        if esperado > 0 and abs(valor - esperado) / esperado > TOLERANCIA_VALOR:
            return False, 'valor informado ({}) nao bate com qtd*preco ({:.2f})'.format(valor, esperado)

    return True, None


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


def formatar_linha_txt(registro):
    return '\t'.join([
        registro['ticker'],
        registro['tipo'],
        '{:.3f}'.format(float(registro['qtd'])),
        registro['data'],
        '{:.3f}'.format(float(registro['preco'])),
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
            item['motivo'] = 'tipo fora do padrao compra/venda: {}'.format(candidato['tipo'])
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
