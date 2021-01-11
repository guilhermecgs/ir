import os
import dropbox
from dropbox import files

OPERATIONS_FILEPATH = 'export_operacoes.txt'


def download_dropbox_file(file_to, file_from=None):
    api_key = os.getenv('DROPBOX_API_KEY')
    if api_key:
        if file_from is None:
            file_from = os.environ['DROPBOX_FILE_LOCATION']
        dbx = dropbox.Dropbox(api_key)
        dbx.files_download_to_file(file_to, file_from)
        try:
            dbx._session.close()
        except:
            pass


def upload_dropbox_file(file_from, file_to=None):
    api_key = os.getenv('DROPBOX_API_KEY')
    if api_key:
        if file_to is None:
            file_to = os.environ['DROPBOX_FILE_LOCATION']
        dbx = dropbox.Dropbox(api_key)
        with open(file_from, 'rb') as f:
            dbx.files_upload(f.read(), file_to, mode=files.WriteMode.overwrite)
        try:
            dbx._session.close()
        except:
            pass
