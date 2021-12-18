import os


class TestUtils():

    def test_must_return_cache_dir_inside_project_root_folder(self):

        from src.utils import CACHE_DIR, pasta_raiz_do_projeto

        assert os.path.isdir(pasta_raiz_do_projeto())
        assert os.path.isdir(os.path.join(pasta_raiz_do_projeto(), 'src'))
        assert CACHE_DIR.endswith('__cache__')

    def test_deve_retornar_ano_corrente_com_dois_digitos(self):
        from src.utils import ano_corrente
        ano = ano_corrente()
        assert type(ano) is str
        assert int(ano) > 20
        assert len(ano) == 2

