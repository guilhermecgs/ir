import smtplib
from email.mime.text import MIMEText
import config


def __smtp_server_config_and_login():
    SMTP_USER = config.SMTP_USER
    SMTP_PASSWORD = config.SMTP_PASSWORD
    SMTP_PORT = config.SMTP_PORT
    SMTP_SERVER = config.SMTP_SERVER

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.ehlo()
    server.login(SMTP_USER, SMTP_PASSWORD)
    return server


def envia_relatorio_txt_por_email(assunto, relatorio):
    if not config.SMTP_SERVER:
        print("Configuração de e-mail não informada.")
        return
    
    to = config.SEND_TO.split(sep=';')

    try:
        server = __smtp_server_config_and_login()
        for to_addrs in to:
            message = 'Subject: {}\n\n{}'.format(assunto, relatorio)
            server.sendmail(config.SMTP_USER, to_addrs, message.encode("utf8"))
        print('Email enviado com sucesso')
        return True
    except Exception as ex:
        print('Erro ao enviar email')
        print(ex)
        raise ex

def envia_relatorio_html_por_email(assunto, relatorio_html):
    SMTP_USER = config.SMTP_USER

    msg = MIMEText(relatorio_html, 'html')
    msg['Subject'] = assunto
    msg['From'] = SMTP_USER
    to = config.SEND_TO.split(sep=';')

    try:
        server = __smtp_server_config_and_login()
        for to_addrs in to:
            msg['To'] = to_addrs
            server.send_message(msg, from_addr=SMTP_USER, to_addrs=to_addrs)
        print('Email enviado com sucesso')
        return True
    except Exception as ex:
        print('Erro ao enviar email')
        print(ex)
        raise ex
