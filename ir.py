import sys
import os
import argparse
import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta

from src.stuff import get_operations_dataframe, \
    calcula_custodia, vendas_no_mes, merge_operacoes, \
    df_to_csv

from src.dropbox_files import upload_dropbox_file, OPERATIONS_FILEPATH


def main(raw_args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--do', required=False)
    args = parser.parse_args(raw_args)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)

    if args.do == 'busca_trades_e_faz_merge_operacoes':
        do_busca_trades_e_faz_merge_operacoes()
        return

    if args.do == 'custodia':
        do_custodia()
        return

    if args.do == 'vendas_no_mes':
        do_vendas_no_mes()
        return

    if args.do == 'envia_relatorio_por_email':
        do_envia_relatorio_por_email()
        return

    do_custodia()


def do_busca_trades_e_faz_merge_operacoes():
    from src.crawler_cei import CrawlerCei
    crawler_cei = CrawlerCei(headless=True)
    df_cei = crawler_cei.busca_trades()

    from src.dropbox_files import download_dropbox_file
    download_dropbox_file()

    df = get_operations_dataframe()
    df = merge_operacoes(df, df_cei)
    df_to_csv(df, OPERATIONS_FILEPATH)

    upload_dropbox_file(OPERATIONS_FILEPATH, os.environ['DROPBOX_FILE_LOCATION'])


def do_custodia():
    from src.dropbox_files import download_dropbox_file
    download_dropbox_file()
    df = calcula_custodia(get_operations_dataframe())
    print(df)
    print('Total na carteira : ' + str(df['valor'].sum()))


def do_envia_relatorio_por_email():
    from src.envia_relatorio_por_email import envia_relatorio_por_email
    envia_relatorio_por_email()


def do_vendas_no_mes():
    from src.dropbox_files import download_dropbox_file
    download_dropbox_file()

    df = get_operations_dataframe()

    data = df['data'].min()
    hoje = datetime.datetime.now().date()
    datas = []

    while data < hoje:
        datas.append(data)
        data = data + relativedelta(months=1)

    datas.append(hoje)

    for data in datas:
        print('Mes: ' + str(data.month) + ' Ano: ' + str(data.year))
        print(vendas_no_mes(df, data.year, data.month))


if __name__ == "__main__":
    main(sys.argv[1:])