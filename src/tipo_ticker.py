from enum import Enum

from src.crawler_yahoo import busca_preco_atual_yahoo
from src.crawler_b3_etfs import e_tipo_etf
import src.crawler_funds_explorer_bs4 as funds_explorer
import src.crawler_fiis as fiis

from cachier import cachier
import datetime

from src.utils import CACHE_DIR


class TipoTicker(Enum):
    FII = 2
    ACAO_OU_ETF = 3
    OPCAO = 4
    FUTURO = 5
    FIP = 6
    FIPIE = 7
    BDR = 8


ticker_map = {
    "ELET6": TipoTicker.ACAO_OU_ETF,
    "ITUB3": TipoTicker.ACAO_OU_ETF,
    "BBASP280W2": TipoTicker.OPCAO,
    "FATN11": TipoTicker.FII,
    "FATN12": TipoTicker.FII,
    "ISAE4": TipoTicker.ACAO_OU_ETF,
    "VALE3": TipoTicker.ACAO_OU_ETF,
    "BBSEC414E": TipoTicker.OPCAO,
    "TAEEC340E": TipoTicker.OPCAO,
    "ELETP415": TipoTicker.OPCAO,
    "BBSEP402": TipoTicker.OPCAO,
    "VALEP555W1": TipoTicker.OPCAO,
    "VALEO540W2": TipoTicker.OPCAO,
    "IVVB11": TipoTicker.ACAO_OU_ETF,
    "EGIEO363": TipoTicker.OPCAO,
    "TAEEC340": TipoTicker.OPCAO,
    "CMIGC119": TipoTicker.OPCAO,
    "ELETO386": TipoTicker.OPCAO,
    "BBSEC414": TipoTicker.OPCAO,
    "RZAT11": TipoTicker.FII,
    "EGIE3": TipoTicker.ACAO_OU_ETF,
    "XPIN11": TipoTicker.FII,
    "HSAF11": TipoTicker.FII,
    "BBSE3": TipoTicker.ACAO_OU_ETF,
    "BBAS3": TipoTicker.ACAO_OU_ETF,
    "CMIG4": TipoTicker.ACAO_OU_ETF,
    "HLOG11": TipoTicker.FII,
    "CXSE3": TipoTicker.ACAO_OU_ETF,
    "TAEE11": TipoTicker.ACAO_OU_ETF,
    "SANB11": TipoTicker.ACAO_OU_ETF,
    "HGRE11": TipoTicker.FII,
    "CLIN11": TipoTicker.FII,
    "AFHI11": TipoTicker.FII,
    "HGBS11": TipoTicker.FII,
    "BPFF11": TipoTicker.FII,
    "RBRL11": TipoTicker.FII,
    "FIGS11": TipoTicker.FII,
    "BCIA11": TipoTicker.FII,
    "CVBI11": TipoTicker.FII,
    "NEWL11": TipoTicker.FII,
    "MCHF11": TipoTicker.FII,
    "RBRP11": TipoTicker.FII,
    "HGLG11": TipoTicker.FII,
    "BARI11": TipoTicker.FII,
    "WHGR11": TipoTicker.FII,
    "FIIB11": TipoTicker.FII,
    "MALL11": TipoTicker.FII,
    "KFOF11": TipoTicker.FII,
    "HGRU11": TipoTicker.FII,
    "CPTR11": TipoTicker.FII,
    "RFOF11": TipoTicker.FII,
    "BTLG11": TipoTicker.FII,
    "HSML11": TipoTicker.FII,
    "VILG11": TipoTicker.FII,
    "BLMR11": TipoTicker.FII,
    "JSRE11": TipoTicker.FII,
    "LGCP11": TipoTicker.FII,
    "HGFF11": TipoTicker.FII,
    "XPCA11": TipoTicker.FII,
    "LVBI11": TipoTicker.FII,
    "TRXF11": TipoTicker.FII,
    "KCRE11": TipoTicker.FII,
    "VGIP11": TipoTicker.FII,
    "AAZQ11": TipoTicker.FII,
    "RZAG11": TipoTicker.FII,
    "JFLL11": TipoTicker.FII,
    "RBRX11": TipoTicker.FII,
    "VGIA11": TipoTicker.FII,
    "RBRY11": TipoTicker.FII,
    "KNRI11": TipoTicker.FII,
    "PLCR11": TipoTicker.FII,
    "MCCI11": TipoTicker.FII,
    "XPLG11": TipoTicker.FII,
    "DEVA11": TipoTicker.FII,
    "IRDM11": TipoTicker.FII,
    "HABT11": TipoTicker.FII,
    "GARE11": TipoTicker.FII,
    "TGAR11": TipoTicker.FII,
    "PQDP11": TipoTicker.FII,
    "PSEC11": TipoTicker.FII,
    "PCIP11": TipoTicker.FII,
    "RBRY12": TipoTicker.FII,
    "RBRP12": TipoTicker.FII,
    "RVBI11": TipoTicker.FII,
    "HFOF11": TipoTicker.FII,
    "RECT11": TipoTicker.FII,
    "TGAR12": TipoTicker.FII,
    "RBGS11": TipoTicker.FII,
    "FVPQ11": TipoTicker.FII,
    "VISC11": TipoTicker.FII,
    "HCTR11": TipoTicker.FII,
    "MAXR11": TipoTicker.FII,
    "ALZR11": TipoTicker.FII,
    "VILG12": TipoTicker.FII,
    "RNGO11": TipoTicker.FII,
    "BBRC11": TipoTicker.FII,
    "SDIL11": TipoTicker.FII,
    "GGRC11": TipoTicker.FII,
    "MXRF11": TipoTicker.FII,
    "RBED11": TipoTicker.FII,
    "FIIP11B": TipoTicker.FII,
    "NSLU11": TipoTicker.FII,
    "BRCR11": TipoTicker.FII,
    "CBOP11": TipoTicker.FII,
    "GRLV11": TipoTicker.FII,
    "EURO11": TipoTicker.FII,
    "SAAG11": TipoTicker.FII,
    "VLOL11": TipoTicker.FII,
    "BBFI11B": TipoTicker.FII,
    "BGRT39": TipoTicker.ACAO_OU_ETF,
    "MSFT34": TipoTicker.ACAO_OU_ETF,
    "CMIGE109": TipoTicker.OPCAO,
    "BBSEQ39": TipoTicker.OPCAO,
    "VALEP532W4": TipoTicker.OPCAO,
    "BRBI11": TipoTicker.ACAO_OU_ETF,
    "DISB34": TipoTicker.ACAO_OU_ETF,
    "ITRI11": TipoTicker.FII,
    "U1BE34": TipoTicker.ACAO_OU_ETF,
    "NVDC34": TipoTicker.ACAO_OU_ETF,
    "MUTC34": TipoTicker.ACAO_OU_ETF,
    "BBFO11": TipoTicker.FII,
    "RBRF11": TipoTicker.FII,
    "AAPL34": TipoTicker.ACAO_OU_ETF,
    "XFIX11": TipoTicker.ACAO_OU_ETF,
    "BABA34": TipoTicker.ACAO_OU_ETF,
    "CMIN3": TipoTicker.ACAO_OU_ETF,
    "VIVA3": TipoTicker.ACAO_OU_ETF,
    "BRAV3": TipoTicker.ACAO_OU_ETF,
    "VULC3": TipoTicker.ACAO_OU_ETF,
    "CSMG3": TipoTicker.ACAO_OU_ETF,
    "CURY3": TipoTicker.ACAO_OU_ETF,
    "RAPT4": TipoTicker.ACAO_OU_ETF,
    "ONCO3": TipoTicker.ACAO_OU_ETF,
    "STBP3": TipoTicker.ACAO_OU_ETF,
    "ANIM3": TipoTicker.ACAO_OU_ETF,
    "AXIA6": TipoTicker.ACAO_OU_ETF,
    "AXIA7": TipoTicker.ACAO_OU_ETF,
    "BOVA11": TipoTicker.ACAO_OU_ETF,
    "ORVR3": TipoTicker.ACAO_OU_ETF,
    "TTEN3": TipoTicker.ACAO_OU_ETF,
    "KEPL3": TipoTicker.ACAO_OU_ETF,
    "RECV3": TipoTicker.ACAO_OU_ETF,
    "RANI3": TipoTicker.ACAO_OU_ETF,
    "ALUP11": TipoTicker.ACAO_OU_ETF,
    "AMER3": TipoTicker.ACAO_OU_ETF,
    "OIBR3": TipoTicker.ACAO_OU_ETF,
    "T1AL34": TipoTicker.ACAO_OU_ETF,
    "E1DU34": TipoTicker.ACAO_OU_ETF,
    "M1TA34": TipoTicker.ACAO_OU_ETF,
    "AMZO34": TipoTicker.ACAO_OU_ETF,
    "GOGL34": TipoTicker.ACAO_OU_ETF,
    "MELI34": TipoTicker.ACAO_OU_ETF,
    "CVBI12": TipoTicker.FII,
    "INBR32": TipoTicker.ACAO_OU_ETF,
    "PETR4": TipoTicker.ACAO_OU_ETF,
    "HGCR11": TipoTicker.FII,
    "ITSA4": TipoTicker.ACAO_OU_ETF,
    "RBVA11": TipoTicker.FII,
    "FPAB11": TipoTicker.FII,
    "EDFO11B": TipoTicker.ACAO_OU_ETF,
    "VRTA11": TipoTicker.FII,
    "CVCB3": TipoTicker.ACAO_OU_ETF,
    "PTBL3": TipoTicker.ACAO_OU_ETF,
    "BCFF11": TipoTicker.FII,
    "KNIP11": TipoTicker.FII,
    "BBPO11": TipoTicker.FII,
}

@cachier(stale_after=datetime.timedelta(days=30), cache_dir=CACHE_DIR)
def tipo_ticker(ticker):

    if ticker in ticker_map:
        return ticker_map[ticker]

    if funds_explorer.eh_tipo_fii(ticker) or fiis.eh_tipo_fii(ticker):
        return TipoTicker.FII

    if e_tipo_etf(ticker):
        return TipoTicker.ACAO_OU_ETF

    if busca_preco_atual_yahoo(ticker):
        return TipoTicker.ACAO_OU_ETF

    from src.crawler_advfn import advfn_tipo_ticker
    return advfn_tipo_ticker(ticker)