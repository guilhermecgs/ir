import hashlib
import pandas as pd


def _hash_params(args, kwargs):
    def _hash(obj):
        if isinstance(obj, pd.DataFrame):
            return hashlib.sha256(pd.util.hash_pandas_object(obj).values.tobytes()).hexdigest()
        return obj

    k_args = tuple(map(_hash, args))
    k_kwargs = tuple(sorted({k: _hash(v) for k, v in kwargs.items()}.items()))
    return k_args + k_kwargs
