from unittest import TestCase

from src.calculo_ir import CalculoIr
from src.stuff import get_operations_dataframe, calcula_custodia
from src.relatorio import relatorio_html, relatorio_txt


class TestRelatorio(TestCase):

    def test_relatorio_html(self):
        from src.dropbox_files import download_dropbox_file
        download_dropbox_file()

        df = get_operations_dataframe()
        df = df.tail(150)

        calcula_custodia(df)
        calculo_ir = CalculoIr(df=df)
        calculo_ir.calcula()

        from py_w3c.validators.html.validator import HTMLValidator

        assert HTMLValidator().validate_fragment(relatorio_html(calculo_ir))


    def test_relatorio_txt(self):
        from src.dropbox_files import download_dropbox_file
        download_dropbox_file()

        df = get_operations_dataframe()
        df = df.tail(150)

        calcula_custodia(df)
        calculo_ir = CalculoIr(df=df)
        calculo_ir.calcula()

        with open("relatorio.txt", "w") as relatorio:
            relatorio.write(relatorio_txt(calculo_ir))

