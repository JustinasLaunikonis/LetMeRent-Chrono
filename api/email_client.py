import smtplib
from email.message import EmailMessage

from api.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    EMAIL_FROM,
)


class EmailClient:
    def send_email(self, to_email, subject, body):
        if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
            print("Email settings are missing.")
            return False

        message = EmailMessage()
        message["From"] = EMAIL_FROM
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(message)

        return True