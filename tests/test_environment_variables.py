import os
import unittest


class TestEnvironmentVariables(unittest.TestCase):

    def test_download_dropbox_file(self):
        print(os.environ)
        assert 'DROPBOX_API_KEY' in os.environ
        assert 'DROPBOX_FILE_LOCATION' in os.environ
        assert 'CPF' in os.environ
        assert 'SENHA_CEI' in os.environ
        assert 'GMAIL_FROM' in os.environ
        assert 'GMAIL_PASSWORD' in os.environ
        assert 'SEND_TO' in os.environ
