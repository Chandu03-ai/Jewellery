from Razor_pay.Services.razorpayClient import client
from Razor_pay.Database.subscriptionDb import upsertSubscriptionData
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse
from yensiAuthentication.mongoData import updateUser
from Razor_pay.Utils.webhookUtils import extractCleanSubscriptionData

def fetchAndProcessSubscription(userId: str, subscriptionId: str):
    """
    Fetches subscription from Razorpay and updates local DB with cleaned data.
    """
    try:
        subscription = client.subscription.fetch(subscriptionId)
        if not subscription:
            logger.error("Subscription with ID %s not found.", subscriptionId)
            return None

        logger.info("Subscription with ID %s fetched successfully.", subscriptionId)

        # Inject userId into notes to ensure downstream compatibility
        subscription["notes"] = subscription.get("notes", {})
        subscription["notes"]["userId"] = userId

        # Extract cleaned subscription data
        minimalData = extractCleanSubscriptionData(subscription)

        # Upsert to DB
        upsertSubscriptionData({"userId": userId, "subscriptionId": subscriptionId}, minimalData)
        logger.info("Subscription data updated in the database.")

        updateUser(
            {"id": userId},
            {
                "userMetadata.paymentSubscription.subscriptionId": subscriptionId,
                "userMetadata.paymentSubscription.planId": minimalData.get("planId"),
                "userMetadata.paymentSubscription.subscriptionStatus": minimalData.get("subscriptionStatus"),
                "userMetadata.paymentSubscription.customerId": minimalData.get("customerId"),
            },
        )

        logger.info("User data updated with new subscription information.")

        return minimalData

    except Exception as e:
        logger.error(f"Error fetching subscription ID {subscriptionId}: {str(e)}", exc_info=True)
        raise e
