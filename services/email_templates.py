# app/services/email_templates.py

def investment_created_email(
    user_name: str,
    uk_inv_id: str,
    invest_date: str,
    invest_time: str,
    tenure_days: int
):
    subject = "Your Investment Has Been Successfully Created"

    body = f"""
Hi {user_name},

Your investment has been successfully created.

Investment ID   : {uk_inv_id}
Investment Date : {invest_date}
Investment Time : {invest_time}
Tenure          : {tenure_days} days

Thank you for investing with us.

Regards,
Investment Team
"""
    return subject, body
