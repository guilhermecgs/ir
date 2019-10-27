import os
import unittest


class TestEnvironmentVariables(unittest.TestCase):

    def test_download_dropbox_file(self):
        assert 'DROPBOX_API_KEY' in os.environ
        assert 'DROPBOX_FILE_LOCATION' in os.environ
