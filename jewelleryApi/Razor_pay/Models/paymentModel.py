from pydantic import BaseModel


class PaymentVerificationPayload(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
