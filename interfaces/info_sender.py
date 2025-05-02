import smtplib
from email.mime.text import MIMEText
from config import settings


def send_email(subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.FROM_EMAIL
    msg["To"] = settings.TARGET_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(settings.FROM_EMAIL, settings.EMAIL_PASSWORD)
        server.send_message(msg)
