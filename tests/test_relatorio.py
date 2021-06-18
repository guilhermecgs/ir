import datetime

from src.calculo_ir import CalculoIr
from src.relatorio import relatorio_html, relatorio_txt
from src.stuff import get_operations, calcula_custodia
from tests.utils import create_testing_dataframe


class TestRelatorio():

    def test_deve_retornar_relatorio_html_com_todos_os_meses(self):
        data = [{'ticker': 'MAXR11', 'qtd': 100, 'data': datetime.date(2019, 3, 11), 'preco': 100,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'PETR4', 'qtd': 100, 'data': datetime.date(2019, 4, 11), 'preco': 100,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'XPLG11', 'qtd': 100, 'data': datetime.date(2019, 4, 12), 'preco': 200,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'XPLG11', 'qtd': -50, 'data': datetime.date(2019, 5, 12), 'preco': 220,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'MAXR11', 'qtd': 100, 'data': datetime.date(2019, 6, 11), 'preco': 100,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'PETR4', 'qtd': 100, 'data': datetime.date(2019, 10, 11), 'preco': 100,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'XPLG11', 'qtd': 100, 'data': datetime.date(2019, 10, 12), 'preco': 200,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'XPLG11', 'qtd': -50, 'data': datetime.date(2019, 11, 12), 'preco': 220,
                 'aquisicao_via': 'HomeBroker'}
                ]

        df = create_testing_dataframe(data)

        calcula_custodia(df)
        calculo_ir = CalculoIr(df=df)
        calculo_ir.calcula()

        from py_w3c.validators.html.validator import HTMLValidator

        html = relatorio_html(calculo_ir)
        assert HTMLValidator().validate_fragment(html)
        assert 'MES : 5/2019' in html
        assert 'MES : 11/2019' in html

    def test_deve_retornar_relatorio_html_apenas_com_os_ultimos_x_meses(self):
        data = [{'ticker': 'MAXR11', 'qtd': 100, 'data': datetime.date(2019, 3, 11), 'preco': 100,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'PETR4', 'qtd': 100, 'data': datetime.date(2019, 4, 11), 'preco': 100,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'XPLG11', 'qtd': 100, 'data': datetime.date(2019, 4, 12), 'preco': 200,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'XPLG11', 'qtd': -50, 'data': datetime.date(2019, 5, 12), 'preco': 220,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'MAXR11', 'qtd': 100, 'data': datetime.date(2019, 6, 11), 'preco': 100,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'PETR4', 'qtd': 100, 'data': datetime.date(2019, 10, 11), 'preco': 100,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'XPLG11', 'qtd': 100, 'data': datetime.date(2019, 10, 12), 'preco': 200,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'XPLG11', 'qtd': -50, 'data': datetime.date(2019, 11, 12), 'preco': 220,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'CMIN3', 'qtd': 300, 'data': datetime.date(2020, 1, 12), 'preco': 220,
                 'aquisicao_via': 'HomeBroker'},
                {'ticker': 'CMIN3', 'qtd': -300, 'data': datetime.date(2020, 2, 12), 'preco': 420,
                 'aquisicao_via': 'HomeBroker'}]

        df = create_testing_dataframe(data)

        calcula_custodia(df)
        calculo_ir = CalculoIr(df=df)
        calculo_ir.calcula()

        from py_w3c.validators.html.validator import HTMLValidator

        html = relatorio_html(calculo_ir, numero_de_meses=2)
        assert HTMLValidator().validate_fragment(html)
        assert 'MES : 5/2019' not in html
        assert 'MES : 11/2019' in html
        assert 'MES : 02/2020' in html

    def test_relatorio_txt(self):
        from src.dropbox_files import download_dropbox_file
        download_dropbox_file()

        df = get_operations()
        df = df.tail(60)

        calcula_custodia(df)
        calculo_ir = CalculoIr(df=df)
        calculo_ir.calcula()

        with open("relatorio.txt", "w") as relatorio:
            relatorio.write(relatorio_txt(calculo_ir))

