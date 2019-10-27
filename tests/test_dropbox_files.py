import os
import unittest
import dropbox

from src.dropbox_files import OPERATIONS_FILEPATH


class TestDropbox(unittest.TestCase):

    def test_download_dropbox_file(self):
        dbx = dropbox.Dropbox(os.environ['DROPBOX_API_KEY'])

        file_location = os.environ['DROPBOX_FILE_LOCATION']

        dbx.files_download_to_file(OPERATIONS_FILEPATH, file_location)

        assert os.path.isfile(OPERATIONS_FILEPATH)
