import dropbox
from dropbox import files
import config

OPERATIONS_FILEPATH = 'export_operacoes.txt'


def download_dropbox_file():
    dbx = dropbox.Dropbox(config.DROPBOX_API_KEY)
    dbx.files_download_to_file(OPERATIONS_FILEPATH, config.DROPBOX_FILE_LOCATION)
    try:
        dbx._session.close()
    except:
        pass


def upload_dropbox_file(file_from, file_to):
    dbx = dropbox.Dropbox(config.DROPBOX_API_KEY)
    with open(file_from, 'rb') as f:
        dbx.files_upload(f.read(), file_to, mode=files.WriteMode.overwrite)
    try:
        dbx._session.close()
    except:
        pass