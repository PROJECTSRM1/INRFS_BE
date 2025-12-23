import random
import smtplib
from email.mime.text import MIMEText
import requests

# Generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Send OTP to Email (Gmail SMTP)
def send_email_otp(to_email: str, otp: str):
    msg = MIMEText(f"Your OTP is: {otp}")
    msg["Subject"] = "Your OTP Code"
    msg["From"] = "yourgmail@gmail.com"
    msg["To"] = to_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("yourgmail@gmail.com", "your-app-password")  # Gmail App Password
    server.send_message(msg)
    server.quit()

# Send OTP to Mobile (Fast2SMS)
def send_mobile_otp(mobile: str, otp: str):
    url = "https://www.fast2sms.com/dev/bulkV2"
    payload = {
        "sender_id": "TXTIND",
        "message": f"Your OTP is: {otp}",
        "route": "v3",
        "numbers": mobile
    }
    headers = {
        "authorization": "your_fast2sms_key"
    }

    response = requests.post(url, data=payload, headers=headers)
    return response.json()
