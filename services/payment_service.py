from fastapi import HTTPException
from utils.razorpay_client import razorpay_client


def create_razorpay_order(investment_id: int, amount: int):
    try:
        order = razorpay_client.order.create({
            "amount": amount * 100,   # INR → paise
            "currency": "INR",
            "receipt": f"investment_{investment_id}",
            "payment_capture": 1
        })

        return {
            "investment_id": investment_id,
            "order_id": order["id"],
            "amount": amount,
            "currency": "INR",
            "razorpay_key": razorpay_client.auth[0]
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def verify_razorpay_payment(
    investment_id: int,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str
):
    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        })

        return {
            "status": "SUCCESS",
            "message": "Payment verified successfully",
            "investment_id": investment_id,
            "payment_id": razorpay_payment_id
        }

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Payment verification failed"
        )
