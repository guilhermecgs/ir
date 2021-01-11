import os
import unittest


class TestEnvironmentVariables(unittest.TestCase):

    @unittest.skipIf(True, "roda os testes separadamente, aqui facilita para chamada do programa principal")
    def test_environment_variables(self):
        test_environment_variables_basic();
        test_environment_variables_smtp();
        test_environment_variables_dropbox();

    def test_environment_variables_basic(self):
        if 'CI_PIPELINE_SOURCE' in os.environ:
            print(os.environ['CI_PIPELINE_SOURCE'])

        assert 'CPF' in os.environ
        assert 'SENHA_CEI' in os.environ

    def test_environment_variables_smtp(self):
        assert 'SMTP_FROM' in os.environ
        # Autenticacao é opcional agora entao tem opção de não passar usuario e senha
        hasUser = ('SMTP_USER' in os.environ)
        hasPassword = ('SMTP_PASSWORD' in os.environ)
        assert (hasUser and hasPassword ) or (not hasUser and not hasPassword)
        assert 'SEND_TO' in os.environ

    @unittest.skipUnless('DROPBOX_API_KEY' in os.environ, "sem configuracao para api dropbox")
    def test_environment_variables_dropbox(self):
        assert 'DROPBOX_API_KEY' in os.environ
        assert 'DROPBOX_FILE_LOCATION' in os.environ
