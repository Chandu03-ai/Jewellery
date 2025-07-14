import json
from fastapi import APIRouter, Request
from ReturnLog.logReturn import returnResponse
from yensiAuthentication import logger
from Razor_pay.Utils.webhookUtils import *
from Razor_pay.Utils.tokenUtils import *
from Razor_pay.Database.subscriptionDb import upsertSubscriptionData
from yensiAuthentication.mongoData import updateUser
from constants import rpwebhookSecret
from Razor_pay.Database.invoiceDb import updateInvoiceData
from Razor_pay.Database.paymentsDb import upsertPayment

router = APIRouter(prefix="/auth", tags=["Razorpay Webhooks"])


@router.post("/webhook/razorpay")
async def razorpayWebhook(request: Request):
    """
    Handles incoming Razorpay webhook events.

    - Verifies the Razorpay signature to ensure request authenticity.
    - Parses the event payload and routes it to the appropriate handler:
        - subscription events → handleSubscriptionEvent
        - invoice events → handleInvoiceEvent
        - payment events → handlePaymentEvent
    - Logs and returns appropriate responses for unhandled events or errors.

    Parameters:
    -----------
    request : Request
        The incoming HTTP request containing the Razorpay webhook payload.

    Returns:
    --------
    JSON response with appropriate status code based on processing result.
    """
    try:
        body = await request.body()
        logger.info("Webhook received")

        signature = request.headers.get("X-Razorpay-Signature", "")
        if not signature:
            logger.warning("Missing Razorpay signature in header")
            return returnResponse(1565)

        if not verifyRazorpaySignature(body, signature, rpwebhookSecret):
            logger.warning("Invalid Razorpay signature. Webhook request rejected.")
            return returnResponse(1564)

        logger.info("Razorpay webhook signature verified")

        event = json.loads(body)
        eventType = event.get("event")
        logger.info(f"Event type received: {eventType}")

        if eventType.startswith("subscription."):
            await handleSubscriptionEvent(event)
        elif eventType.startswith("invoice."):
            await handleInvoiceEvent(event)
        elif eventType.startswith("payment."):
            await handlePaymentEvent(event)

        else:
            logger.info(f"Event '{eventType}' not handled explicitly")

            return returnResponse(1551, result={"eventType": eventType})

    except Exception as e:
        logger.error(f"Exception during webhook processing: {str(e)}")
        return returnResponse(1552)


async def handleSubscriptionEvent(event):
    """
    Processes Razorpay subscription webhook events.

    - Extracts subscription data from the event payload.
    - Updates subscription info in the database.
    - Updates user metadata with subscription details.
    - Allocates tokens if the event type is 'subscription.charged'.

    Parameters:
    -----------
    event : dict
        The webhook payload from Razorpay containing subscription details.

    Returns:
    --------
    None
    """
    try:
        eventType = event["event"]
        logger.info(f"[Subscription Event] Event Type: {eventType}")

        subscription = event.get("payload", {}).get("subscription", {}).get("entity", {})
        if not subscription:
            logger.warning("No subscription entity found in webhook payload")
            return

        subscriptionData = extractCleanSubscriptionData(subscription, eventType)
        logger.info(f"[Subscription Event] Extracted subscription data: {subscriptionData}")

        subscriptionId = subscriptionData.get("subscriptionId")
        userId = subscriptionData.get("userId")
        if not userId:
            logger.warning(f"[Subscription Event] userId missing for subscriptionId: {subscriptionId}")
            return

        logger.info(f"[Subscription Event] Handling subscription update for userId: {userId}, subscriptionId: {subscriptionId}")

        update_data = {
            "planId": subscriptionData.get("planId"),
            "customerId": subscriptionData.get("customerId"),
            "subscriptionStatus": subscriptionData.get("subscriptionStatus"),
            "tokensAllocated": subscriptionData.get("tokensAllocated"),
            "subscriptionStartTime": subscriptionData.get("subscriptionStartTime"),
            "subscriptionEndTime": subscriptionData.get("subscriptionEndTime"),
            "nextBillingDate": subscriptionData.get("nextBillingDate"),
            "authExpiryTime": subscriptionData.get("authExpiryTime"),
            "customerNotify": subscriptionData.get("customerNotify"),
            "authPaymentUrl": subscriptionData.get("authPaymentUrl"),
            "completedBillingCycles": subscriptionData.get("completedBillingCycles"),
            "remainingBillingCycles": subscriptionData.get("remainingBillingCycles"),
            "userCount": subscriptionData.get("userCount"),
        }

        update_data = {k: v for k, v in update_data.items() if v is not None}
        logger.debug(f"[Subscription Event] Pre-clean update data successfully")

        upsertSubscriptionData(
            {"userId": userId, "subscriptionId": subscriptionId},
            update_data
        )
        logger.info(f"[Subscription Event] Subscription data upserted to DB for subscriptionId: {subscriptionId}")

        updateUser(
            {"id": userId},
            {
                "userMetadata.paymentSubscription.subscriptionStatus": subscriptionData.get("subscriptionStatus"),
                "userMetadata.paymentSubscription.planId": subscriptionData.get("planId"),
                "userMetadata.paymentSubscription.subscriptionId": subscriptionId,
                "userMetadata.paymentSubscription.customerId": subscriptionData.get("customerId"),
            }
        )
        logger.info(f"[Subscription Event] User metadata updated for userId: {userId}")

        status = subscriptionData.get("subscriptionStatus")
        logger.info(f"[Subscription Event] Final subscription status for {subscriptionId}: {status}")

        if eventType == "subscription.charged":
            logger.info(f"[Subscription Event] Subscription {subscriptionId} is charged. Proceeding with token allocation.")
            allocateTokensOnSubscription(subscriptionData)
        else:
            logger.info(f"[Subscription Event] No token allocation. Current subscription status: {status}")

    except Exception as e:
        logger.error(f"[Subscription Event] Exception occurred while processing: {str(e)}", exc_info=True)



async def handleInvoiceEvent(event):
    """
    Processes Razorpay invoice webhook events.

    - Extracts invoice data from the event payload.
    - Updates the invoice record in the database.

    Parameters:
    -----------
    event : dict
        The webhook payload from Razorpay containing invoice details.

    Returns:
    --------
    None
    """
    eventType = event["event"]
    logger.info(f"[Invoice Event] Event Type: {eventType}")
    invoice = event["payload"]["invoice"]["entity"]
    invoiceData = extractCleanInvoiceData(invoice, eventType)

    invoiceId = invoiceData.get("invoiceId")
    logger.info(f"Invoice: {invoiceId}, Status: {invoiceData['status']}, Amount: {invoiceData['amountPaid']}")

    result = updateInvoiceData({"invoiceId": invoiceId}, invoiceData)
    logger.info(f"Invoice update status: {result['status']}")



async def handlePaymentEvent(event):
    """
    Processes Razorpay payment webhook events.

    - Extracts payment data from the event payload.
    - Upserts the payment record into the database.

    Parameters:
    -----------
    event : dict
        The webhook payload from Razorpay containing payment details.

    Returns:
    --------
    None
    """
    eventType = event["event"]
    logger.info(f"[Payment Event] Event Type: {eventType}")

    payment = event["payload"]["payment"]["entity"]
    paymentData = extractCleanPaymentData(payment, eventType)

    paymentId = paymentData.get("paymentId")
    upsertPayment(paymentId, paymentData)
