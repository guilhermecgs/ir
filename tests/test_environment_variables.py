import os
import unittest


class TestEnvironmentVariables(unittest.TestCase):

    def test_environment_variables(self):
        if 'CI_PIPELINE_SOURCE' in os.environ:
            print(os.environ['CI_PIPELINE_SOURCE'])

        assert 'DROPBOX_API_KEY' in os.environ
        assert 'DROPBOX_FILE_LOCATION' in os.environ
        assert 'CPF' in os.environ
        assert 'SENHA_CEI' in os.environ
        assert 'GMAIL_FROM' in os.environ
        assert 'GMAIL_PASSWORD' in os.environ
        assert 'SEND_TO' in os.environ
