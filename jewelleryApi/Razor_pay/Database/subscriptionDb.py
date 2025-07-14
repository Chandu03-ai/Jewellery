from Razor_pay.Database.db import subscriptionCollection


def insertSubscriptionData(subscriptionData: dict):
    try:
        data = subscriptionCollection.insert_one(subscriptionData)
        subscriptionData.pop("_id", None)
        return data
    except Exception as e:
        raise Exception(f"Failed to insert subscription data: {e}")


def getSubscriptionById(query: dict):
    try:
        data = subscriptionCollection.find_one(query)
        if not data:
            return None
        data.pop("_id", None)  # Remove MongoDB's default _id field
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch subscription by ID: {e}")


def upsertSubscriptionData(query: dict, updateData: dict):
    try:
        result = subscriptionCollection.update_one(query, {"$set": updateData},upsert=True)
        return result.modified_count
    except Exception as e:
        raise Exception(f"Failed to update subscription: {e}")


def listSubscriptions(query: dict):
    try:
        subscriptions = list(subscriptionCollection.find(query))
        for item in subscriptions:
            item.pop("_id", None)
        return subscriptions  # Will return empty list if none found
    except Exception as e:
        raise Exception(f"[listSubscriptions] Failed to list subscriptions: {str(e)}")


def cancelSubscription(subscriptionId: str):
    try:
        result = subscriptionCollection.update_one({"subscriptionId": subscriptionId}, {"$set": {"status": "cancelled"}})
        return result.modified_count
    except Exception as e:
        raise Exception(f"Failed to cancel subscription: {e}")


