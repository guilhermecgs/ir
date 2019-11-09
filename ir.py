import sys
import argparse
import datetime
from dateutil.relativedelta import relativedelta

from src.stuff import get_operations_dataframe, calcula_custodia, vendas_no_mes


def main(raw_args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--do', required=True)
    args = parser.parse_args(raw_args)

    if args.do == 'custodia':
        do_custodia()

    if args.do == 'vendas_no_mes':
        do_custodia()

def do_custodia():
    from src.dropbox_files import download_dropbox_file
    download_dropbox_file()
    print(calcula_custodia(get_operations_dataframe()))

def do_vendas_no_mes():
    from src.dropbox_files import download_dropbox_file
    download_dropbox_file()

    hoje = datetime.datetime.now().date()

    datas = [hoje + relativedelta(months=-i) for i in range(1, 6)]
    for data in datas:
        print('Mes: ' + str(data.month) + ' Ano: ' + str(data.year))
        print(vendas_no_mes(get_operations_dataframe(), data.year, data.month))

if __name__ == "__main__":
    main(sys.argv[1:])