import os
import smtplib
from email.mime.text import MIMEText


def envia_relatorio_txt_por_email(assunto, relatorio):
    gmail_user = os.environ['GMAIL_FROM']
    gmail_password = os.environ['GMAIL_PASSWORD']
    to = os.environ['SEND_TO'].split(sep=';')

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)

        message = 'Subject: {}\n\n{}'.format(assunto, relatorio)
        server.sendmail(gmail_user, to, message.encode("utf8"))
        server.quit()
        print('Email enviado com sucesso')
        return True
    except Exception as ex:
        print('Erro ao enviar email')
        print(ex)
        raise ex


def envia_relatorio_html_por_email(assunto, relatorio_html):
    gmail_user = os.environ['GMAIL_FROM']
    gmail_password = os.environ['GMAIL_PASSWORD']
    to = os.environ['SEND_TO'].split(sep=';')

    msg = MIMEText(relatorio_html, 'html')
    msg['Subject'] = assunto
    msg['From'] = gmail_user

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        for to_addrs in to:
            msg['To'] = to_addrs
            server.send_message(msg, from_addr=gmail_user, to_addrs=to_addrs)
        print('Email enviado com sucesso')
        return True
    except Exception as ex:
        print('Erro ao enviar email')
        print(ex)
        raise ex
