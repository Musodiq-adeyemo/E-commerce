from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from typing import Dict


class Evns:
    MAIL_SERVER ="smtp_mail.outlook.com"
    MAIL_PORT = 587
    MAIL_USERNAME = "sirmuso@gmail.com"
    MAIL_PASSWORD = "musawdeeq"
    MAIL_FROM = "sirmuso@gmail.com"
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,

config = ConnectionConfig(
    MAIL_SERVER = Evns.MAIL_SERVER,
    MAIL_PORT = Evns.MAIL_PORT,
    MAIL_USERNAME = Evns.MAIL_USERNAME,
    MAIL_PASSWORD = Evns.MAIL_PASSWORD,
    MAIL_FROM = Evns.MAIL_FROM,
    USE_CREDENTIALS= True,
    MAIL_STARTTLS= False,
    MAIL_SSL_TLS= False
)
def send_registration_mail(subject:str,email_to:str,body:Dict):
    message = MessageSchema (
        subject= subject,
        recipients=[email_to],
        template_body= body,
        subtype= "html"
    )
    fm = FastMail(config)
    return fm.send_message(message=message)

def password_reset(subject:str,email_to:str,body:Dict):
    message = MessageSchema (
        subject= subject,
        recipients=[email_to],
        template_body= body,
        subtype="html"
    )
    fm = FastMail(config)
    return fm.send_message(message=message)
