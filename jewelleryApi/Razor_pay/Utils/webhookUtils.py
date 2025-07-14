from yensiAuthentication import logger
import hmac
import hashlib
from Razor_pay.Utils.util import convertEpochToCycleData

def verifyRazorpaySignature(body: bytes, signature: str, secret: str) -> bool:
    try:
        logger.info("Starting Razorpay signature verification...")

        generated = hmac.new(
            key=secret.encode(),
            msg=body,
            digestmod=hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(generated, signature):
            logger.info("Razorpay signature verified successfully.")
            return True
        else:
            logger.warning("Razorpay signature verification failed.")
            return False

    except Exception as e:
        logger.error("Error while verifying Razorpay signature.")
        logger.exception(e)
        return False

def extractCleanSubscriptionData(subscription: dict, eventType: str = None) -> dict:
    """
    Extract and format Razorpay subscription webhook data to match DB schema.
    """
    logger.info("[Extract Subscription] Starting extraction")
    
    notes = subscription.get("notes", {})
    planId = subscription.get("plan_id")
    customerId = subscription.get("customer_id")
    userId = notes.get("userId")
    tokens = int(notes.get("tokens", 0))
    userCount = subscription.get("quantity", 1)
    nextBillingDate = convertEpochToCycleData(subscription["charge_at"])["givenTime"] if subscription.get("charge_at") else None
    subscriptionStartTime = convertEpochToCycleData(subscription["start_at"])["givenTime"] if subscription.get("start_at") else None
    subscriptionEndTime = convertEpochToCycleData(subscription["end_at"])["givenTime"] if subscription.get("end_at") else None


    logger.debug(f"[Extract Subscription] Extracted all the info of user: {userId}")
    
    subscriptionData = {
        "userId": userId,
        "customerId": customerId,
        "planId": planId,
        "subscriptionId": subscription.get("id"),
        "subscriptionStatus": subscription.get("status"),
        "tokensAllocated": tokens,
        "userCount": userCount,
        "subscriptionStartTime": subscriptionStartTime,
        "subscriptionEndTime": subscriptionEndTime,
        "nextBillingDate": nextBillingDate,
        "totalBillingCycles": subscription.get("total_count"),
        "completedBillingCycles": subscription.get("paid_count"),
        "remainingBillingCycles": subscription.get("remaining_count"),
        "authExpiryTime": subscription.get("expire_by"),
        "customerNotify": subscription.get("customer_notify"),
        "authPaymentUrl": subscription.get("short_url"),
        "subscriptionNotes": notes,
        "eventType": eventType,
    }

    cleanData = {k: v for k, v in subscriptionData.items() if v is not None}

    logger.info("[Extract Subscription] Cleaned subscription data ready for DB insertion")
    return cleanData




def extractCleanInvoiceData(invoice: dict, eventType: str) -> dict:
    """
    Extracts and returns only essential, non-confidential fields from Razorpay invoice payload.
    Includes paymentId for linking invoice to payment record.
    """
    invoiceData = {
        "invoiceId": invoice.get("id"),
        "subscriptionId": invoice.get("subscription_id"),
        "customerId": invoice.get("customer_id"),
        "orderId": invoice.get("order_id"),
        "paymentId": invoice.get("payment_id"), 
        "status": invoice.get("status"),
        "amount": invoice.get("amount"),
        "amountPaid": invoice.get("amount_paid"),
        "amountDue": invoice.get("amount_due"),
        "currency": invoice.get("currency"),
        "taxAmount": invoice.get("tax_amount"),
        "taxableAmount": invoice.get("taxable_amount"),
        "grossAmount": invoice.get("gross_amount"),
        "issuedAt": invoice.get("issued_at"),
        "paidAt": invoice.get("paid_at"),
        "createdAt": invoice.get("created_at"),
        "eventType": eventType,
        "type": invoice.get("type"),
    }

    return {k: v for k, v in invoiceData.items() if v is not None}



def extractCleanPaymentData(payment: dict, eventType: str) -> dict:
    """
    Extract and return all relevant (including confidential) fields from Razorpay payment payload.
    Safely handle missing fields and errors.
    """
    paymentData = {
        "paymentId": payment.get("id"),
        "status": payment.get("status"),
        "method": payment.get("method"),
        "amount": payment.get("amount"),
        "currency": payment.get("currency"),
        "orderId": payment.get("order_id"),
        "invoiceId": payment.get("invoice_id"),
        "createdAt": payment.get("created_at"),
        "captured": payment.get("captured"),
        "customerId": payment.get("customer_id"),
        "email": payment.get("email"),
        "contact": payment.get("contact"),
        "tokenId": payment.get("token_id"),
        "cardId": payment.get("card_id"),
        "fee": payment.get("fee"),
        "tax": payment.get("tax"),
        "eventType": eventType,
    }

    # Optional card info (safe)
    card = payment.get("card", {})
    if card:
        paymentData["card"] = {
            "last4": card.get("last4"),
            "network": card.get("network"),
            "type": card.get("type"),
            "issuer": card.get("issuer"),
            "expiryMonth": card.get("expiry_month"),
            "expiryYear": card.get("expiry_year"),
        }

    # Error details for failed payments
    if payment.get("status") == "failed":
        paymentData["error"] = {
            "code": payment.get("error_code"),
            "description": payment.get("error_description"),
            "source": payment.get("error_source"),
            "step": payment.get("error_step"),
            "reason": payment.get("error_reason"),
        }

    # Remove None values
    return {k: v for k, v in paymentData.items() if v is not None}

