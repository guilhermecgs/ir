import os
import smtplib


def envia_relatorio_txt_por_email(assunto, relatorio):
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


def envia_relatorio_html_por_email(assunto, relatorio_txt, relatorio_html):
    import smtplib

    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    gmail_user = os.environ['GMAIL_FROM']
    gmail_password = os.environ['GMAIL_PASSWORD']
    to = os.environ['SEND_TO'].split(sep=';')

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = assunto
    msg['From'] = gmail_user
    msg['To'] = to

    # Create the body of the message (a plain-text and an HTML version).
    text = relatorio_txt
    html = relatorio_html

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.send_message(msg, from_addr=gmail_user, to_addrs=to)

        print('Email enviado com sucesso')
        return True
    except Exception as ex:
        print('Erro ao enviar email')
        print(ex)
        return False
