from fastapi import APIRouter
from schemas.payment_schema import CreateOrderRequest, VerifyPaymentRequest
from services.payment_service import (
    create_razorpay_order,
    verify_razorpay_payment
)

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/create-order")
def create_order(data: CreateOrderRequest):
    return create_razorpay_order(
        investment_id=data.investment_id,
        amount=data.amount
    )


@router.post("/verify")
def verify_payment(data: VerifyPaymentRequest):
    return verify_razorpay_payment(
        investment_id=data.investment_id,
        razorpay_order_id=data.razorpay_order_id,
        razorpay_payment_id=data.razorpay_payment_id,
        razorpay_signature=data.razorpay_signature
    )
