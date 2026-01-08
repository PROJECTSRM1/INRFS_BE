from pydantic import BaseModel

class CreateOrderRequest(BaseModel):
    investment_id: int
    amount: int  # INR

class VerifyPaymentRequest(BaseModel):
    investment_id: int
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
