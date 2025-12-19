import smtplib
from os import environ as env
from datetime import datetime

SMTP_DOMAIN = env.get("SMTP_DOMAIN")
SMTP_PORT = env.get("SMTP_PORT")
EMAIL_SENDER = env.get("EMAIL_SENDER")
EMAIL_PASSWORD = env.get("EMAIL_PASSWORD")

SUBJECT = "Fire Alert - High Temperature Detected"

CONTENT = '''
    Fire alert!

    Temperature has exceeded the safe limit.

    Please check immediately.

    - IoT Monitoring System
'''

text = f"Subject: {SUBJECT}\n\n{CONTENT}"

class Notification:
    def __init__(self):
        self.last_send_email = datetime.min

    def send_email(self, email_receiver: str) -> None:
        with smtplib.SMTP(SMTP_DOMAIN, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, email_receiver, text)
