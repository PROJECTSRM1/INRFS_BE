import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail,content
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")


def send_email(to_email: str, subject: str, body: str, is_html: bool = False):
    if not SENDGRID_API_KEY or not FROM_EMAIL:
        raise RuntimeError("SendGrid configuration missing")

    if is_html:
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=body,  # send as HTML
        )
    else:
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body,  # default plain text
        )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        print("SendGrid error:", e)
        raise
