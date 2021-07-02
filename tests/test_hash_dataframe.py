import pandas as pd
from src.dataframe_hash import _hash_params


class TestHashDataframe():

    def test_deve_criar_hash_de_dataframe(self):
        df_a = pd.DataFrame.from_dict(dict(a=[0], b=[2], c=[3]))
        df_b = pd.DataFrame.from_dict(dict(a=[0], b=[2], c=[3]))
        value_a = _hash_params([df_a, 1], {})
        value_b = _hash_params([df_b, 1], {})

        assert value_a == value_b
