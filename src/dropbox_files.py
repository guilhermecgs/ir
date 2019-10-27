import os
import dropbox


OPERATIONS_FILEPATH = 'export_operacoes.txt'


def download_dropbox_file():
    dbx = dropbox.Dropbox(os.environ['DROPBOX_API_KEY'])
    dbx.files_download_to_file(OPERATIONS_FILEPATH, os.environ['DROPBOX_FILE_LOCATION'])