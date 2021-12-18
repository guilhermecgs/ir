import os
from pathlib import Path


def ano_corrente():
    import time
    return time.strftime("%y", time.localtime())


def pasta_raiz_do_projeto():
    return str(Path(__file__).parent.parent)


CACHE_DIR = os.path.join(pasta_raiz_do_projeto(), '__cache__')