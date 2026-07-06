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
