import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")


def send_email(to_email: str, subject: str, body: str):
    if not SENDGRID_API_KEY or not FROM_EMAIL:
        raise RuntimeError("SendGrid configuration missing")

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body,
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        print("SendGrid error:", e)
        raise





















# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# import os

# # from flask.cli import load_dotenv
# from dotenv import load_dotenv
# load_dotenv()

# def send_email(to_email: str, subject: str, body: str):
#     smtp_host = os.getenv("SMTP_HOST")
#     smtp_port = int(os.getenv("SMTP_PORT"))
#     smtp_user = os.getenv("SMTP_USER")
#     smtp_password = os.getenv("SMTP_PASSWORD")

#     # Hard fail if config missing
#     if not smtp_user or not smtp_password:
#         raise RuntimeError("SMTP credentials not configured properly")

#     msg = MIMEMultipart()
#     msg["From"] = smtp_user
#     msg["To"] = to_email
#     msg["Subject"] = subject

#     msg.attach(MIMEText(body, "plain"))

#     with smtplib.SMTP(smtp_host, smtp_port) as server:
#         server.starttls()
#         server.login(smtp_user, smtp_password)
#         server.send_message(msg)
