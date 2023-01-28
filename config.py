from prettyconf import config

DROPBOX_FILE_LOCATION = config("DROPBOX_FILE_LOCATION")
DROPBOX_API_KEY = config("DROPBOX_API_KEY")
SMTP_USER = config("SMTP_USER", default="smtp_user@abc.com")
SMTP_PASSWORD = config("SMTP_PASSWORD", default="smtp_pass")
SEND_TO = config("SEND_TO", default="emaildestinatario@abc.com")
SMTP_SERVER = config("SMTP_SERVER", default=None)
SMTP_PORT = config("SMTP_PORT", default=2525, cast=int)
CPF = config("CPF", default=None)
SENHA_CEI = config("SENHA_CEI", default=None)