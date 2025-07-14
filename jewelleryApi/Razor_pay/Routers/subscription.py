from fastapi import APIRouter, Request
from Razor_pay.Models.subscriptionModels import SubscriptionUpdateRequest, SubscriptionRequest
from Razor_pay.Services.razorpayClient import client
from yensiAuthentication import logger
from Razor_pay.Database.subscriptionDb import *
from Razor_pay.Database.plansDb import getPlanById
from ReturnLog.logReturn import returnResponse
from Razor_pay.Utils.subscriptionUtils import fetchAndProcessSubscription
from Razor_pay.Utils.webhookUtils import extractCleanSubscriptionData

router = APIRouter(prefix="/subscriptions", tags=["Subscription Service"])

@router.get("/all")
def getAllSubscriptions(request: Request):
    """
    Fetches all active subscriptions for the current user.

    - Extracts userId from the request.
    - Retrieves all subscription records for that user from the database.

    Returns:
    - 1520 on success with a list of subscriptions.
    - 1521 on failure to fetch data.
    """
    try:
        userId = request.state.userMetadata.get("id")
        logger.info("Received request to fetch active subscriptions for user")

        subscriptions = listSubscriptions({"userId": userId})
        logger.info("Fetched active subscriptions from database")

        return returnResponse(1520, result=subscriptions)

    except Exception as e:
        logger.error("Failed to fetch subscriptions. Error: %s", str(e))
        return returnResponse(1521)


@router.post("/checkout")
def createCheckout(request: Request, payload: SubscriptionRequest):
    """
    Creates a Razorpay subscription for the user.

    - Adds userId and token info to subscription notes.
    - Creates the subscription via Razorpay API.
    - Extracts and stores minimal subscription data in the database.

    Returns:
    - 1516 on success with JSON including `authPaymentUrl` to complete the payment.
    - 1538 if the plan is not found.
    - 1517 on any failure during creation.
    """
    try:
        userId = request.state.userMetadata.get("id")
        logger.info("Initiating Razorpay subscription checkout process")

        data = payload.model_dump()
        logger.info("Parsed subscription request payload")

        if "notes" not in data or not isinstance(data["notes"], dict):
            logger.info("'notes' field missing or invalid; initializing notes dictionary")
            data["notes"] = {}

        data["notes"]["userId"] = userId
        logger.info("Attached userId to Razorpay notes")

        plan = getPlanById(payload.plan_id)
        if not plan:
            logger.error("Plan not found in database")
            return returnResponse(1538)

        if payload.subscriptionType is None:
            data["notes"]["subscriptionType"] = "solo"
        else:
            data["notes"]["subscriptionType"] = payload.subscriptionType
            if payload.subscriptionType != "solo":
                if getattr(payload, "teamName", None):
                    teamName = payload.teamName
                else:
                    teamName = f"team_{str(userId)[len(str(userId)) // 2:]}"
                data["notes"]["teamName"] = teamName

        data.pop("subscriptionType", None)
        data.pop("teamName", None)

        logger.info("Plan found successfully")

        subscription = client.subscription.create(data)
        if not subscription or "id" not in subscription:
            logger.error("Razorpay subscription creation failed")
            return returnResponse(1517)

        logger.info("Razorpay subscription created successfully")

        # Attach tokens to notes for downstream usage
        tokens = int(plan.get("notes", {}).get("tokens", 0))
        subscription["notes"] = subscription.get("notes", {})
        subscription["notes"]["tokens"] = tokens

        logger.debug("Attached tokens to notes: %s", tokens)
        # Extract and clean subscription data
        minimalData = extractCleanSubscriptionData(subscription)
        logger.info("Extracted and cleaned subscription data")

        # Insert into DB
        upsertSubscriptionData({"userId": userId, "subscriptionId": subscription["id"]}, minimalData)
        logger.info("Inserted subscription data into database")

        return returnResponse(1516, result=minimalData)

    except Exception as e:
        logger.error(f"Checkout creation failed: {str(e)}", exc_info=True)
        return returnResponse(1517)


@router.get("/fetch/{subscriptionId}")
def fetchSubscription(request: Request, subscriptionId: str):
    """
    Fetches a specific subscription for the current user.

    - Extracts userId from the request.
    - Retrieves the subscription data by subscriptionId and userId from the database.

    Parameters:
    - subscriptionId (str): ID of the subscription to fetch.

    Returns:
    - 1518 on success with subscription data.
    - 1519 on failure to fetch data.
    """
    try:
        userId = request.state.userMetadata.get("id")
        logger.info("Received request to fetch a subscription")

        subscriptionData = fetchAndProcessSubscription(userId,subscriptionId)

        logger.info("Fetched subscription data from database")

        return returnResponse(1518, result=subscriptionData)

    except Exception as e:
        logger.error("Failed to fetch subscription. Error: %s", str(e))
        return returnResponse(1519)


@router.post("/cancel/{subscriptionId}")
def cancelSubscription(request: Request, subscriptionId: str, cancel_at_cycle_end: bool = True):
    try:
        logger.info("Received request to cancel a subscription")

        cancellation = client.subscription.cancel(subscriptionId, {"cancel_at_cycle_end": cancel_at_cycle_end})

        logger.info("Subscription cancellation processed by Razorpay")

        return returnResponse(1522, result={"subscriptionId": cancellation["id"], "status": cancellation["status"]})

    except Exception as e:
        logger.error("Failed to cancel subscription. Error: %s", str(e))
        return returnResponse(1523)


@router.post("/update")
def updateSubscription(request: Request, payload: SubscriptionUpdateRequest):
    try:
        userId = request.state.userMetadata.get("id")
        logger.info("Received request to update a subscription")

        updateData = payload.model_dump(exclude_unset=True)
        subscriptionId = updateData.pop("subscriptionId")

        logger.info("Sending subscription update request to Razorpay")

        updated = client.subscription.edit(subscriptionId, updateData)

        logger.info("Fetching updated subscription data from database")

        data = fetchAndProcessSubscription(userId=userId, subscriptionId=subscriptionId)

        logger.info("Subscription update flow completed")

        return returnResponse(1524, result=data)

    except Exception as e:
        logger.error("Subscription update failed. Error: %s", str(e))
        return returnResponse(1525)


@router.post("/pause/{subscriptionId}")
def pauseSubscription(subscriptionId: str, request: Request):
    try:
        userId = request.state.userMetadata.get("id")
        logger.info("Received request to pause a subscription")
        subscription = getSubscriptionById({"subscriptionId": subscriptionId, "userId": userId})
        if not subscription:
            logger.error("Subscription not found in database")
            return returnResponse(1568)

        paused = client.subscription.pause(subscriptionId, {"pause_at": "now"})

        logger.info("Subscription pause request sent to Razorpay")
        return returnResponse(1534, result={"subscriptionId": paused["id"], "status": paused["status"]})

    except Exception as e:
        logger.error("Failed to pause subscription. Error: %s", str(e))
        return returnResponse(1535)


@router.post("/resume/{subscriptionId}")
def resumeSubscription(request: Request, subscriptionId: str):
    try:
        userId = request.state.userMetadata.get("id")
        logger.info("Received request to resume a subscription")
        subscription = getSubscriptionById({"subscriptionId": subscriptionId, "userId": userId})
        if not subscription:
            logger.error("Subscription not found in database")
            return returnResponse(1568)
        resumed = client.subscription.resume(subscriptionId, {"resume_at": "now"})

        logger.info("Subscription resume request sent to Razorpay")
        return returnResponse(1536, result={"subscriptionId": resumed["id"], "status": resumed["status"]})

    except Exception as e:
        logger.error("Failed to resume subscription. Error: %s", str(e))
        return returnResponse(1537)
