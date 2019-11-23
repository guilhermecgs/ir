import datetime
import os
import unittest

from src.dropbox_files import OPERATIONS_FILEPATH, upload_dropbox_file, download_dropbox_file


class TestDropbox(unittest.TestCase):

    def test_download_dropbox_file(self):
        if os.path.exists(OPERATIONS_FILEPATH):
            os.remove(OPERATIONS_FILEPATH)

        download_dropbox_file()

        assert os.path.isfile(OPERATIONS_FILEPATH)

    def test_upload_dropbox_file(self):
        TEMP_TEST_FILE = 'temp_test_file.txt'
        TEMP_TEST_FILE_UPLOADED = r'/uploaded' + TEMP_TEST_FILE

        with open(TEMP_TEST_FILE, 'w') as file:
            file.write("...test..." + str(datetime.datetime.now()))

        upload_dropbox_file(os.path.abspath(TEMP_TEST_FILE), TEMP_TEST_FILE_UPLOADED)