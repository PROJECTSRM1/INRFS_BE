import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# from flask.cli import load_dotenv
from dotenv import load_dotenv
load_dotenv()

def send_email(to_email: str, subject: str, body: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    # Hard fail if config missing
    if not smtp_user or not smtp_password:
        raise RuntimeError("SMTP credentials not configured properly")

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
