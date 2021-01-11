import os
import smtplib
from email.mime.text import MIMEText

def prepare_smtp():
    smtp_user = os.getenv('SMTP_USER',os.environ['SMTP_FROM'])
    smtp_password = os.getenv('SMTP_PASSWORD')
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = os.getenv('SMTP_PORT', 465)
    if smtp_port == 465:
        server = smtplib.SMTP_SSL(smtp_host, smtp_port)
    else:
        server = smtplib.SMTP(smtp_host, smtp_port)
    server.ehlo()
    if smtp_user and smtp_password:
        server.login(smtp_user, smtp_password)
    return server


def envia_relatorio_txt_por_email(assunto, relatorio):
    if os.getenv('SEND_TO'):
        to = os.environ['SEND_TO'].split(sep=';')
        from_user = os.environ['SMTP_FROM']

        print('enviando relatório simples via email para : ' + str(to))

        try:
            server = prepare_smtp()

            message = 'Subject: {}\n\n{}'.format(assunto, relatorio)
            server.sendmail(from_user, to, message.encode("utf8"))
            server.quit()
            print('Email enviado com sucesso')
            return True
        except Exception as ex:
            print('Erro ao enviar email')
            print(ex)
            return False


def envia_relatorio_html_por_email(assunto, relatorio_html):
    if os.getenv('SEND_TO'):
        to = os.environ['SEND_TO'].split(sep=';')
        from_user = os.environ['SMTP_FROM']

        print('enviando relatório html via email para : ' + str(to))

        msg = MIMEText(relatorio_html, 'html')
        msg['Subject'] = assunto
        msg['From'] = from_user

        try:
            server = prepare_smtp()
            for to_addrs in to:
                msg['To'] = to_addrs
                server.send_message(msg, from_addr=from_user, to_addrs=to_addrs)
            print('Email enviado com sucesso')
            return True
        except Exception as ex:
            print('Erro ao enviar email')
            print(ex)
            return False
