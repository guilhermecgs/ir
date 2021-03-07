import os


class TestUtils():

    def test_must_return_cache_dir_inside_project_root_folder(self):

        from src.utils import CACHE_DIR, pasta_raiz_do_projeto

        assert os.path.isdir(pasta_raiz_do_projeto())
        assert os.path.isdir(os.path.join(pasta_raiz_do_projeto(), 'src'))
        assert CACHE_DIR.endswith('__cache__')
