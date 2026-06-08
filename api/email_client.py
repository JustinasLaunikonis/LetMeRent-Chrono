from flask_mailman import EmailMessage
from api.config import EMAIL_FROM


class EmailClient:
    def send_email(self, to_email, subject, body):
        msg = EmailMessage(
            subject=subject,
            body=body,
            from_email=EMAIL_FROM,
            to=[to_email],
        )

        msg.send()
        return True