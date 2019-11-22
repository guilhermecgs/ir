import argparse
import os
import sys

import pandas as pd

from src.calculo_ir import CalculoIr
from src.dropbox_files import upload_dropbox_file, OPERATIONS_FILEPATH
from src.stuff import get_operations_dataframe, \
    calcula_custodia, merge_operacoes, \
    df_to_csv


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

    if args.do == 'memoria_de_calculo_ir':
        do_calculo_ir()
        return

    if args.do == 'envia_relatorio_por_email':
        do_envia_relatorio_por_email()
        return

    do_calculo_ir()


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


def do_calculo_ir():
    from src.dropbox_files import download_dropbox_file
    download_dropbox_file()

    df = get_operations_dataframe()

    memoria_de_calculo_ir = CalculoIr(df=df)
    memoria_de_calculo_ir.calcula()

    from src.relatorio import report_txt
    report_txt(memoria_de_calculo_ir)
    pass


if __name__ == "__main__":
    main(sys.argv[1:])