import argparse
import os
import sys

import pandas as pd

from src.calculo_ir import CalculoIr
from src.dropbox_files import upload_dropbox_file, OPERATIONS_FILEPATH
from src.envia_relatorio_por_email import envia_relatorio_txt_por_email, envia_relatorio_html_por_email
from src.relatorio.relatorio import relatorio_txt, relatorio_html
from src.stuff import get_operations_dataframe, \
    merge_operacoes, \
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

    if args.do == 'check_environment_variables':
        do_check_environment_variables()
        return

    if args.do == 'calculo_ir':
        do_calculo_ir()
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


def do_check_environment_variables():
    from tests.test_environment_variables import TestEnvironmentVariables
    TestEnvironmentVariables().test_environment_variables()


def do_calculo_ir():
    from src.dropbox_files import download_dropbox_file
    download_dropbox_file()
    df = get_operations_dataframe()

    calculo_ir = CalculoIr(df=df)
    calculo_ir.calcula()

    print(relatorio_txt(calculo_ir))

    envia_relatorio_html_por_email('Calculo de IR - ' + calculo_ir.mes_do_relatorio + ' - CPF: ' + os.environ['CPF'],
                                   relatorio_txt(calculo_ir),
                                   relatorio_html(calculo_ir))


if __name__ == "__main__":
    main(sys.argv[1:])