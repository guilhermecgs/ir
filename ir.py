import sys
import argparse

from src.stuff import get_operations_dataframe, calcula_custodia


def main(raw_args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--do', required=True)
    args = parser.parse_args(raw_args)

    if args.do == 'custodia':
        do_custodia()


def do_custodia():
    from src.dropbox_files import download_dropbox_file
    download_dropbox_file()
    print(calcula_custodia(get_operations_dataframe()))


if __name__ == "__main__":
    main(sys.argv[1:])