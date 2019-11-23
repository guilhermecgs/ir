import os
import smtplib


def envia_relatorio_por_email(assunto, relatorio):
    gmail_user = os.environ['GMAIL_FROM']
    gmail_password = os.environ['GMAIL_PASSWORD']
    to = os.environ['SEND_TO'].split(sep=';')

    print('enviando email para : ' + str(to))

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
        return False